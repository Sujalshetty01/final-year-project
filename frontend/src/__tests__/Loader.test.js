import { render } from '@testing-library/react';
import Loader from '../components/common/Loader';

test('renders Loader without crashing', () => {
  render(<Loader />);
});
