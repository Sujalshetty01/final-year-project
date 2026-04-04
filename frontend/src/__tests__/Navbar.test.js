import { render, screen } from '@testing-library/react';
import Navbar from '../components/Navbar';

test('renders Navbar', () => {
  render(<Navbar />);
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});
