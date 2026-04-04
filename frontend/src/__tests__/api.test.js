import { uploadFile } from '../services/api';

describe('uploadFile', () => {
  it('throws error for unsupported file type', async () => {
    const file = new File(['dummy'], 'test.txt', { type: 'text/plain' });
    await expect(uploadFile(file)).rejects.toThrow('Unsupported file type');
  });
});
