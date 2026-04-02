import { render, screen } from "@testing-library/react";
import ResultsDisplay from "../components/ResultsDisplay";

describe("ResultsDisplay", () => {
  it("renders result label and confidence", () => {
    const result = { label: "Malware", confidence: 0.95 };
    render(<ResultsDisplay result={result} />);
    expect(screen.getByText(/malware/i)).toBeInTheDocument();
    expect(screen.getByText(/95.00%/i)).toBeInTheDocument();
  });
});
