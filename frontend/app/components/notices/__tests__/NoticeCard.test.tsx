import React from 'react';
import { render } from '@testing-library/react-native';
import NoticeCard from '../NoticeCard';

describe('NoticeCard Component', () => {
  const mockNotice = {
    id: '1',
    category: 'Admission',
    title: 'Test Admission Notice',
    date: '2023-10-01',
    description: 'This is a test notice description.',
    isCritical: true,
  };

  it('renders correctly with given notice data', () => {
    const { getByText } = render(<NoticeCard notice={mockNotice as any} />);
    
    expect(getByText('Admission')).toBeTruthy();
    expect(getByText('Test Admission Notice')).toBeTruthy();
    expect(getByText('중요')).toBeTruthy();
  });

  it('does not render "중요" badge if isCritical is false', () => {
    const noticeWithoutCritical = { ...mockNotice, isCritical: false };
    const { queryByText } = render(<NoticeCard notice={noticeWithoutCritical as any} />);
    
    expect(queryByText('중요')).toBeNull();
  });
});
