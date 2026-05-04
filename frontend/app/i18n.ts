import type { LanguageOption, NoticeCategory } from './types';

type TranslationKey =
  | 'tabs.home'
  | 'tabs.chat'
  | 'tabs.notices'
  | 'tabs.calendar'
  | 'headers.chat'
  | 'headers.notices'
  | 'headers.calendar'
  | 'settings.title'
  | 'settings.subtitle'
  | 'settings.profile.title'
  | 'settings.profile.subtitle'
  | 'settings.language.title'
  | 'settings.language.subtitle'
  | 'settings.notifications.title'
  | 'settings.notifications.subtitle'
  | 'settings.logout.title'
  | 'settings.logout.subtitle'
  | 'settings.logout.alertTitle'
  | 'settings.logout.alertMessage'
  | 'settings.logout.cancel'
  | 'settings.language.screenTitle'
  | 'settings.language.screenSubtitle'
  | 'settings.language.korean'
  | 'settings.language.english'
  | 'settings.language.koreanSubtitle'
  | 'settings.language.englishSubtitle'
  | 'settings.language.current'
  | 'menu.information'
  | 'menu.visa'
  | 'menu.topik'
  | 'menu.register'
  | 'menu.scholarship'
  | 'menu.life'
  | 'category.all'
  | 'category.Visa'
  | 'category.TOPIK'
  | 'category.Academic'
  | 'category.Events'
  | 'category.Scholarship'
  | 'category.Dormitory'
  | 'notices.imageAttachment'
  | 'notices.important'
  | 'notices.deadline'
  | 'notices.posted'
  | 'notices.saveDeadline'
  | 'notices.removeFromCalendar'
  | 'notices.emptyTitle'
  | 'notices.emptyDescription'
  | 'home.todayNotices'
  | 'home.todayNoticesEmpty'
  | 'home.todayDeadlines'
  | 'home.todayDeadlinesEmpty'
  | 'home.weeklyTasks'
  | 'home.weeklyTasksHint'
  | 'home.weeklyTasksEmpty'
  | 'home.progress'
  | 'home.completed'
  | 'home.remaining'
  | 'home.urgent'
  | 'home.done';

const translations: Record<LanguageOption, Record<TranslationKey, string>> = {
  Korean: {
    'tabs.home': '홈',
    'tabs.chat': '채팅',
    'tabs.notices': '공지',
    'tabs.calendar': '캘린더',
    'headers.chat': '챗봇 상담',
    'headers.notices': '공지사항',
    'headers.calendar': '캘린더',
    'settings.title': '설정',
    'settings.subtitle': '프로필, 언어, 알림 설정을 관리해보세요.',
    'settings.profile.title': '내 프로필',
    'settings.profile.subtitle': '입학 및 개인 정보를 확인하고 수정해요',
    'settings.language.title': '언어',
    'settings.language.subtitle': '앱에서 사용할 언어를 선택해요',
    'settings.notifications.title': '알림 설정',
    'settings.notifications.subtitle': '중요 카테고리와 알림 빈도를 관리해요',
    'settings.logout.title': '로그아웃',
    'settings.logout.subtitle': '앱에서 로그아웃해요',
    'settings.logout.alertTitle': '로그아웃',
    'settings.logout.alertMessage': '정말 로그아웃할까요?',
    'settings.logout.cancel': '취소',
    'settings.language.screenTitle': '언어 설정',
    'settings.language.screenSubtitle': '앱에서 사용할 언어를 선택해보세요',
    'settings.language.korean': '한국어',
    'settings.language.english': '영어',
    'settings.language.koreanSubtitle': '앱 화면을 한국어로 표시합니다.',
    'settings.language.englishSubtitle': '앱 화면을 영어로 표시합니다.',
    'settings.language.current': '현재 언어',
    'menu.information': '정보',
    'menu.visa': '비자',
    'menu.topik': 'TOPIK',
    'menu.register': '입학',
    'menu.scholarship': '장학금',
    'menu.life': '생활',
    'category.all': '전체',
    'category.Visa': '비자',
    'category.TOPIK': 'TOPIK',
    'category.Academic': '입학',
    'category.Events': '행사',
    'category.Scholarship': '장학금',
    'category.Dormitory': '기숙사',
    'notices.imageAttachment': '이미지 첨부',
    'notices.important': '중요',
    'notices.deadline': '마감일',
    'notices.posted': '게시일',
    'notices.saveDeadline': '마감일 저장',
    'notices.removeFromCalendar': '캘린더에서 제거',
    'notices.emptyTitle': '공지사항이 없습니다',
    'notices.emptyDescription': '선택한 카테고리에 표시할 공지가 없습니다.',
    'home.todayNotices': '이번주 공지',
    'home.todayNoticesEmpty': '최근 일주일 동안 올라온 공지가 없습니다.',
    'home.todayDeadlines': '오늘 마감 공지',
    'home.todayDeadlinesEmpty': '오늘 마감으로 저장된 공지가 없습니다.',
    'home.weeklyTasks': '이번 주 할 일',
    'home.weeklyTasksHint':
      '캘린더에 저장한 공지 중 이번 주까지 처리해야 할 중요한 일정입니다.',
    'home.weeklyTasksEmpty': '이번 주까지 처리할 저장 공지가 없습니다.',
    'home.progress': '진행률',
    'home.completed': '완료',
    'home.remaining': '남음',
    'home.urgent': '긴급',
    'home.done': '완료',
  },
  English: {
    'tabs.home': 'Home',
    'tabs.chat': 'Chat',
    'tabs.notices': 'Notices',
    'tabs.calendar': 'Calendar',
    'headers.chat': 'Chatbot',
    'headers.notices': 'Notices',
    'headers.calendar': 'Calendar',
    'settings.title': 'Settings',
    'settings.subtitle': 'Manage your profile, language, and notifications.',
    'settings.profile.title': 'My Profile',
    'settings.profile.subtitle': 'Check and edit your admission and personal information.',
    'settings.language.title': 'Language',
    'settings.language.subtitle': 'Choose the language used in the app.',
    'settings.notifications.title': 'Notifications',
    'settings.notifications.subtitle': 'Manage important categories and notification frequency.',
    'settings.logout.title': 'Logout',
    'settings.logout.subtitle': 'Sign out of the app.',
    'settings.logout.alertTitle': 'Logout',
    'settings.logout.alertMessage': 'Are you sure you want to logout?',
    'settings.logout.cancel': 'Cancel',
    'settings.language.screenTitle': 'Language Settings',
    'settings.language.screenSubtitle': 'Choose the language used in the app.',
    'settings.language.korean': 'Korean',
    'settings.language.english': 'English',
    'settings.language.koreanSubtitle': 'Display the app in Korean.',
    'settings.language.englishSubtitle': 'Display the app in English.',
    'settings.language.current': 'Current Language',
    'menu.information': 'Information',
    'menu.visa': 'Visa',
    'menu.topik': 'TOPIK',
    'menu.register': 'Register',
    'menu.scholarship': 'Scholarship',
    'menu.life': 'Life',
    'category.all': 'All',
    'category.Visa': 'Visa',
    'category.TOPIK': 'TOPIK',
    'category.Academic': 'Academic',
    'category.Events': 'Events',
    'category.Scholarship': 'Scholarship',
    'category.Dormitory': 'Dormitory',
    'notices.imageAttachment': 'Image attached',
    'notices.important': 'Important',
    'notices.deadline': 'Deadline',
    'notices.posted': 'Posted',
    'notices.saveDeadline': 'Save deadline',
    'notices.removeFromCalendar': 'Remove from calendar',
    'notices.emptyTitle': 'No notices',
    'notices.emptyDescription': 'There are no notices in the selected category.',
    'home.todayNotices': "This Week's Notices",
    'home.todayNoticesEmpty': 'No notices posted in the last week.',
    'home.todayDeadlines': "Today's Deadlines",
    'home.todayDeadlinesEmpty': 'No saved notices due today.',
    'home.weeklyTasks': 'This Week',
    'home.weeklyTasksHint':
      'Important saved notices that should be handled by the end of this week.',
    'home.weeklyTasksEmpty': 'No saved notices to handle this week.',
    'home.progress': 'Progress',
    'home.completed': 'Completed',
    'home.remaining': 'Remaining',
    'home.urgent': 'Urgent',
    'home.done': 'Done',
  },
};

export function t(language: LanguageOption, key: TranslationKey) {
  return translations[language][key];
}

export function getCategoryLabel(
  language: LanguageOption,
  category: NoticeCategory | 'All'
) {
  return category === 'All'
    ? t(language, 'category.all')
    : t(language, `category.${category}` as TranslationKey);
}
