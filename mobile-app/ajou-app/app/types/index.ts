import type React from 'react';

export type NoticeCategory =
  | 'Visa'
  | 'TOPIK'
  | 'Academic'
  | 'Events'
  | 'Scholarship'
  | 'Dormitory';

export type LanguageOption = 'English' | 'Korean';

export type StudentType =
  | 'Undergraduate'
  | 'Graduate'
  | 'Exchange / Visiting';

export type AcademicStatus =
  | 'Enrolled'
  | 'On Leave'
  | 'Completed Coursework';

export type ResidenceType = 'Dormitory' | 'Off-campus';

export type NotificationFrequency = 'Low' | 'Medium' | 'High';

export type Notice = {
  id: string;
  title: string;
  category: NoticeCategory;
  summary: string;
  date: string;
  deadline?: string;
  hasAttachmentOnly?: boolean;
  isCritical?: boolean;
  description?: string;
  link?: string;
};

export type Task = {
  id: string;
  title: string;
  dueDate: string;
  category: NoticeCategory | 'General';
  isDone: boolean;
  progress?: number;
};

export type SavedNoticeReminder = {
  id: string;
  noticeId: string;
  title: string;
  dueDate: string;
  category: NoticeCategory;
  summary: string;
  link?: string;
  isDone: boolean;
  savedAt: string;
};

export type UserProfileStatus = {
  schoolEmail: string;
  studentType: StudentType;
  academicStatus: AcademicStatus;
  year: string;
  semester: string;
  studentId: string;
  visaType: string;
  preferredLanguage: LanguageOption;
  residenceType: ResidenceType;
  topikStatus: string;
  gpa: string;
  major: string;
  interests: NoticeCategory[];
};

export type AppContextType = {
  userProfileStatus: UserProfileStatus;
  setUserProfileStatus: React.Dispatch<React.SetStateAction<UserProfileStatus>>;

  selectedLanguage: LanguageOption;
  setSelectedLanguage: React.Dispatch<React.SetStateAction<LanguageOption>>;

  selectedNoticeCategories: NoticeCategory[];
  setSelectedNoticeCategories: React.Dispatch<
    React.SetStateAction<NoticeCategory[]>
  >;

  notificationFrequency: NotificationFrequency;
  setNotificationFrequency: React.Dispatch<
    React.SetStateAction<NotificationFrequency>
  >;

  notices: Notice[];
  setNotices: React.Dispatch<React.SetStateAction<Notice[]>>;
  noticesLoading: boolean;
  noticesError: string | null;
  refreshNotices: () => Promise<void>;
  savedNoticeReminders: SavedNoticeReminder[];
  addNoticeReminder: (notice: Notice) => void;
  removeNoticeReminder: (noticeId: string) => void;
  toggleNoticeReminder: (notice: Notice) => void;
  toggleNoticeReminderDone: (reminderId: string) => void;

  tasks: Task[];
  setTasks: React.Dispatch<React.SetStateAction<Task[]>>;
};
