"""Evaluate trained GNN and baseline models and generate report (JSON + PDF).

Produces: metrics.json, confusion_matrix.png, roc_curve.png, evaluation_report.pdf
"""
import argparse
import os
import json
import numpy as np
import torch
import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support, roc_auc_score, confusion_matrix, roc_curve)
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import os


def load_data(path):
    try:
        data = torch.load(path)
    except Exception:
        data = torch.load(path, weights_only=False)
    return np.array(data['X']), np.array(data['y'])


def evaluate(gnn_model_path, data_path, out_dir):
    X, y = load_data(data_path)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # load model (assumes same SimpleGNN architecture)
    from train_gnn import SimpleGNN
    sample = X[0]
    in_feats = sample.shape[-1]
    model = SimpleGNN(in_feats=in_feats)
    model.load_state_dict(torch.load(gnn_model_path, map_location=device))
    model.to(device).eval()

    logits = []
    trues = []
    with torch.no_grad():
        for xb, yb in zip(X, y):
            xb_t = torch.tensor(np.expand_dims(xb, 0), dtype=torch.float32).to(device)
            out = model(xb_t)
            logits.append(torch.softmax(out, dim=1).cpu().numpy()[0])
            trues.append(int(yb))

    probs = np.array([p[1] for p in logits])
    preds = (probs >= 0.5).astype(int)

    acc = accuracy_score(trues, preds)
    prec, recall, f1, _ = precision_recall_fscore_support(trues, preds, average='binary')
    try:
        auc = roc_auc_score(trues, probs)
    except Exception:
        auc = None

    cm = confusion_matrix(trues, preds)

    os.makedirs(out_dir, exist_ok=True)
    metrics = {'accuracy': acc, 'precision': float(prec), 'recall': float(recall), 'f1': float(f1), 'roc_auc': None if auc is None else float(auc)}
    with open(os.path.join(out_dir, 'metrics.json'), 'w') as fh:
        json.dump(metrics, fh, indent=2)

    # confusion matrix plot
    plt.figure()
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.savefig(os.path.join(out_dir, 'confusion_matrix.png'))
    plt.close()

    # ROC
    if auc is not None:
        fpr, tpr, _ = roc_curve(trues, probs)
        plt.figure()
        plt.plot(fpr, tpr, label=f'ROC AUC={auc:.3f}')
        plt.plot([0,1],[0,1],'--', color='gray')
        plt.xlabel('FPR')
        plt.ylabel('TPR')
        plt.legend()
        plt.savefig(os.path.join(out_dir, 'roc_curve.png'))
        plt.close()

    # build a simple PDF
    pdf_path = os.path.join(out_dir, 'evaluation_report.pdf')
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont('Helvetica', 12)
    c.drawString(72, 720, 'Evaluation Report')
    c.drawString(72, 700, f'Accuracy: {metrics["accuracy"]:.4f}')
    c.drawString(72, 684, f'Precision: {metrics["precision"]:.4f}')
    c.drawString(72, 668, f'Recall: {metrics["recall"]:.4f}')
    c.drawString(72, 652, f'F1: {metrics["f1"]:.4f}')
    if metrics.get('roc_auc') is not None:
        c.drawString(72, 636, f'ROC-AUC: {metrics["roc_auc"]:.4f}')
    c.drawString(72, 600, 'Confusion matrix and ROC curve included as figures.')
    # embed images
    try:
        c.drawImage(os.path.join(out_dir, 'confusion_matrix.png'), 72, 360, width=200, height=200)
    except Exception:
        pass
    try:
        if os.path.exists(os.path.join(out_dir, 'roc_curve.png')):
            c.drawImage(os.path.join(out_dir, 'roc_curve.png'), 300, 360, width=200, height=200)
    except Exception:
        pass
    c.showPage()
    c.save()

    print('Wrote metrics and PDF to', out_dir)

    # Baseline comparison: train a RandomForest on pooled node features
    try:
        # pool node features by mean if needed
        X_arr = np.array([np.mean(x, axis=0) if x.ndim==2 else x for x in X])
        X_train, X_test, y_train, y_test = train_test_split(X_arr, y, test_size=0.2, random_state=42, stratify=y)
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        rf_probs = rf.predict_proba(X_test)[:,1]
        rf_preds = (rf_probs >= 0.5).astype(int)
        rf_acc = accuracy_score(y_test, rf_preds)
        rf_prec, rf_recall, rf_f1, _ = precision_recall_fscore_support(y_test, rf_preds, average='binary')
        try:
            rf_auc = roc_auc_score(y_test, rf_probs)
        except Exception:
            rf_auc = None

        # Bootstrap AUC difference (GNN vs RF) on test split
        # recompute GNN probs on X_test
        gnn_probs_test = []
        from train_gnn import SimpleGNN
        sample = X[0]
        model = SimpleGNN(in_feats=sample.shape[-1])
        model.load_state_dict(torch.load(gnn_model_path, map_location=device))
        model.to(device).eval()
        with torch.no_grad():
            for xb in X_test:
                xb_t = torch.tensor(np.expand_dims(xb, 0), dtype=torch.float32).to(device)
                out = model(xb_t)
                gnn_probs_test.append(torch.softmax(out, dim=1).cpu().numpy()[0][1])
        gnn_probs_test = np.array(gnn_probs_test)

        if len(gnn_probs_test) == len(rf_probs):
            n_boot = 1000
            diffs = []
            idxs = np.arange(len(gnn_probs_test))
            for _ in range(n_boot):
                s = np.random.choice(idxs, size=len(idxs), replace=True)
                try:
                    a = roc_auc_score(y_test[s], gnn_probs_test[s])
                    b = roc_auc_score(y_test[s], rf_probs[s])
                    diffs.append(a - b)
                except Exception:
                    continue
            diffs = np.array(diffs)
            ci_low, ci_high = np.percentile(diffs, [2.5, 97.5]) if len(diffs)>0 else (None, None)
            p_val = (np.sum(diffs <= 0) + 1) / (len(diffs) + 1) if len(diffs)>0 else None
            boot_stats = {'n_boot': int(len(diffs)), 'diff_mean': float(np.mean(diffs)) if len(diffs)>0 else None, 'ci': [ci_low, ci_high], 'p_value': float(p_val) if p_val is not None else None}

            comp = {'rf': {'accuracy': rf_acc, 'precision': float(rf_prec), 'recall': float(rf_recall), 'f1': float(rf_f1), 'roc_auc': None if rf_auc is None else float(rf_auc)}, 'bootstrap_auc_difference': boot_stats}
            with open(os.path.join(out_dir, 'baseline_comparison.json'), 'w') as fh:
                json.dump(comp, fh, indent=2)

            # append summary to PDF
            try:
                ext_pdf_path = os.path.join(out_dir, 'evaluation_report_extended.pdf')
                c = canvas.Canvas(ext_pdf_path, pagesize=letter)
                c.setFont('Helvetica', 11)
                c.drawString(72, 740, 'Extended Evaluation: GNN vs RandomForest')
                c.drawString(72, 720, f'GNN ROC-AUC: {metrics.get("roc_auc")}')
                c.drawString(72, 704, f'RF ROC-AUC: {rf_auc}')
                if boot_stats:
                    c.drawString(72, 688, f'Bootstrap AUC diff mean: {boot_stats.get("diff_mean")}')
                    c.drawString(72, 672, f'95% CI: {boot_stats.get("ci")} p-value approx: {boot_stats.get("p_value")}')

                # Include viva notes (if present) as an additional page in the extended report
                try:
                    viva_path = os.path.join(os.path.dirname(__file__), 'viva_notes.md')
                    if os.path.exists(viva_path):
                        with open(viva_path, 'r', encoding='utf-8') as vf:
                            viva_text = vf.read()
                        # write a page with wrapped text
                        textobj = c.beginText(72, 600)
                        textobj.setFont('Helvetica', 10)
                        import textwrap
                        for paragraph in viva_text.split('\n\n'):
                            for line in textwrap.wrap(paragraph, width=90):
                                textobj.textLine(line)
                            textobj.textLine('')
                        c.drawText(textobj)
                        # also write a machine-friendly summary file
                        try:
                            summary_path = os.path.join(out_dir, 'viva_summary.txt')
                            with open(summary_path, 'w', encoding='utf-8') as sf:
                                sf.write(viva_text)
                        except Exception:
                            pass
                except Exception:
                    pass

                c.showPage()
                c.save()
            except Exception:
                pass

    except Exception as e:
        print('Baseline comparison skipped or failed:', e)


def cli():
    p = argparse.ArgumentParser()
    p.add_argument('--gnn', required=True)
    p.add_argument('--data', required=True)
    p.add_argument('--out', default='out/eval')
    args = p.parse_args()
    evaluate(args.gnn, args.data, args.out)


if __name__ == '__main__':
    cli()
