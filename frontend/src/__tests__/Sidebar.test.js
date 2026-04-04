import { render, screen } from '@testing-library/react';
import Sidebar from '../components/Sidebar';

test('renders Sidebar', () => {
  render(<Sidebar />);
  expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
});
