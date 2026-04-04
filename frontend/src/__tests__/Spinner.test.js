import { render } from '@testing-library/react';
import Spinner from '../components/Spinner';

test('renders Spinner without crashing', () => {
  render(<Spinner />);
});
