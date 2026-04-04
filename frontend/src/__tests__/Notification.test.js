import { render, screen } from '@testing-library/react';
import Notification from '../components/common/Notification';

test('renders notification message', () => {
  render(<Notification message="Test notification" type="success" />);
  expect(screen.getByText(/Test notification/i)).toBeInTheDocument();
});
