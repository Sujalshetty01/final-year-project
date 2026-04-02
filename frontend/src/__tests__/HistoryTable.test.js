import { render, screen, fireEvent } from "@testing-library/react";
import HistoryTable from "../components/HistoryTable";

describe("HistoryTable", () => {
  it("renders history rows and handles click", () => {
    const history = [
      { id: 1, filename: "file1.pcap", date: "2026-03-29", label: "Benign", confidence: 0.87 },
    ];
    const onSelect = jest.fn();
    render(<HistoryTable history={history} onSelect={onSelect} />);
    expect(screen.getByText(/file1.pcap/i)).toBeInTheDocument();
    fireEvent.click(screen.getByText(/file1.pcap/i));
    expect(onSelect).toHaveBeenCalledWith(history[0]);
  });
});
