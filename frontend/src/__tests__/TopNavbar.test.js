import { render, screen } from '@testing-library/react';
import TopNavbar from '../components/TopNavbar';

test('renders TopNavbar', () => {
  render(<TopNavbar />);
  expect(screen.getByRole('banner')).toBeInTheDocument();
});
