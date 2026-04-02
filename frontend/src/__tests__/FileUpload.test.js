import { render, screen, fireEvent } from "@testing-library/react";
import FileUpload from "../components/FileUpload";

describe("FileUpload", () => {
  it("renders and triggers file select", () => {
    const onFileSelect = jest.fn();
    render(<FileUpload onFileSelect={onFileSelect} loading={false} />);
    const button = screen.getByText(/browse/i);
    expect(button).toBeInTheDocument();
    fireEvent.click(button);
  });
});
