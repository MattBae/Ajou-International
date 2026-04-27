import React, { createContext, ReactNode, useContext, useEffect, useState } from 'react';
import { fetchNotices } from '../services/notices';
import type {
    AppContextType,
    LanguageOption,
    Notice,
    NoticeCategory,
    NotificationFrequency,
    SavedNoticeReminder,
    Task,
    UserProfileStatus,
} from '../types';

const initialUserProfileStatus: UserProfileStatus = {
  name: 'Student',
  email: 'student@example.com',
  languageInstituteStatus: 'Planned',
  languageInstituteTerm: 'Term 1',
  targetAdmissionTerm: 'September',
  desiredMajor: 'Digital Media',
  visaType: 'D-2',
  visaExpiryDate: '2026-08-31',
  visaExpiryUnknown: false,
  topikStatus: 'None',
  topikLevel: 'Level 4',
  topikTargetLevel: 'Level 4',
  topikTestPlan: 'Scheduled',
  interests: ['Visa', 'TOPIK', 'Admission'],
  preferredLanguage: 'English',
  residenceType: 'Dormitory',
};

const initialSelectedLanguage: LanguageOption = 'English';

const initialSelectedNoticeCategories: NoticeCategory[] = [
  'Visa',
  'TOPIK',
  'Academic',
];

const initialNotificationFrequency: NotificationFrequency = 'Medium';

const initialTasks: Task[] = [
  {
    id: 't1',
    title: 'Prepare visa extension documents',
    dueDate: '2026-04-09',
    category: 'Visa',
    isDone: false,
    progress: 60,
  },
  {
    id: 't2',
    title: 'Check TOPIK application date',
    dueDate: '2026-04-11',
    category: 'TOPIK',
    isDone: false,
    progress: 20,
  },
  {
    id: 't3',
    title: 'Review course registration changes',
    dueDate: '2026-04-08',
    category: 'Academic',
    isDone: true,
    progress: 100,
  },
  {
    id: 't4',
    title: 'Plan weekly schedule',
    dueDate: '2026-04-13',
    category: 'General',
    isDone: false,
    progress: 40,
  },
];

function normalizeReminderDate(dateText: string) {
  const normalized = dateText.trim().replace(/\./g, '-');
  const match = normalized.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);

  if (!match) {
    return new Date().toISOString().slice(0, 10);
  }

  const [, year, month, day] = match;
  return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
}

function getReminderDueDate(notice: Notice) {
  return normalizeReminderDate(notice.deadline ?? notice.date);
}

const AppContext = createContext<AppContextType | undefined>(undefined);

type AppProviderProps = {
  children: ReactNode;
};

export function AppProvider({ children }: AppProviderProps) {
  const [userProfileStatus, setUserProfileStatus] = useState<UserProfileStatus>(
    initialUserProfileStatus
  );
  const [selectedLanguage, setSelectedLanguage] =
    useState<LanguageOption>(initialSelectedLanguage);
  const [selectedNoticeCategories, setSelectedNoticeCategories] = useState<
    NoticeCategory[]
  >(initialSelectedNoticeCategories);
  const [notificationFrequency, setNotificationFrequency] =
    useState<NotificationFrequency>(initialNotificationFrequency);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [noticesLoading, setNoticesLoading] = useState(true);
  const [noticesError, setNoticesError] = useState<string | null>(null);
  const [savedNoticeReminders, setSavedNoticeReminders] = useState<
    SavedNoticeReminder[]
  >([]);
  const [tasks, setTasks] = useState<Task[]>(initialTasks);

  async function refreshNotices() {
    try {
      setNoticesLoading(true);
      setNoticesError(null);

      const nextNotices = await fetchNotices();
      setNotices(nextNotices);
    } catch (error) {
      setNoticesError(
        error instanceof Error ? error.message : 'Failed to load notices.'
      );
    } finally {
      setNoticesLoading(false);
    }
  }

  useEffect(() => {
    void refreshNotices();
  }, []);

  useEffect(() => {
    if (notices.length === 0) {
      return;
    }

    setSavedNoticeReminders((prev) =>
      prev.map((reminder) => {
        const matchedNotice = notices.find((notice) => notice.id === reminder.noticeId);

        if (!matchedNotice) {
          return reminder;
        }

        const nextDueDate = getReminderDueDate(matchedNotice);

        if (nextDueDate === reminder.dueDate) {
          return reminder;
        }

        return {
          ...reminder,
          dueDate: nextDueDate,
        };
      })
    );
  }, [notices]);

  function addNoticeReminder(notice: Notice) {
    setSavedNoticeReminders((prev) => {
      if (prev.some((item) => item.noticeId === notice.id)) {
        return prev;
      }

      const reminder: SavedNoticeReminder = {
        id: `reminder-${notice.id}`,
        noticeId: notice.id,
        title: notice.title,
        dueDate: getReminderDueDate(notice),
        category: notice.category,
        summary: notice.summary,
        link: notice.link,
        isDone: false,
        savedAt: new Date().toISOString(),
      };

      return [...prev, reminder].sort((a, b) => a.dueDate.localeCompare(b.dueDate));
    });
  }

  function removeNoticeReminder(noticeId: string) {
    setSavedNoticeReminders((prev) =>
      prev.filter((item) => item.noticeId !== noticeId)
    );
  }

  function toggleNoticeReminder(notice: Notice) {
    setSavedNoticeReminders((prev) => {
      if (prev.some((item) => item.noticeId === notice.id)) {
        return prev.filter((item) => item.noticeId !== notice.id);
      }

      const reminder: SavedNoticeReminder = {
        id: `reminder-${notice.id}`,
        noticeId: notice.id,
        title: notice.title,
        dueDate: getReminderDueDate(notice),
        category: notice.category,
        summary: notice.summary,
        link: notice.link,
        isDone: false,
        savedAt: new Date().toISOString(),
      };

      return [...prev, reminder].sort((a, b) => a.dueDate.localeCompare(b.dueDate));
    });
  }

  function toggleNoticeReminderDone(reminderId: string) {
    setSavedNoticeReminders((prev) =>
      prev.map((item) =>
        item.id === reminderId
          ? {
              ...item,
              isDone: !item.isDone,
            }
          : item
      )
    );
  }

  return (
    <AppContext.Provider
      value={{
        userProfileStatus,
        setUserProfileStatus,
        selectedLanguage,
        setSelectedLanguage,
        selectedNoticeCategories,
        setSelectedNoticeCategories,
        notificationFrequency,
        setNotificationFrequency,
        notices,
        setNotices,
        noticesLoading,
        noticesError,
        refreshNotices,
        savedNoticeReminders,
        addNoticeReminder,
        removeNoticeReminder,
        toggleNoticeReminder,
        toggleNoticeReminderDone,
        tasks,
        setTasks,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);

  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }

  return context;
}
