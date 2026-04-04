import { render, screen } from '@testing-library/react';
import FileUpload from '../components/FileUpload';

test('renders FileUpload button', () => {
  render(<FileUpload />);
  expect(screen.getByText(/Upload/i)).toBeInTheDocument();
});
