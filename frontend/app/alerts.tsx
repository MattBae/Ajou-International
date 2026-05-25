import Ionicons from '@expo/vector-icons/Ionicons';
import { useRouter } from 'expo-router';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAppContext } from './context/AppContext';
import { getCategoryLabel, t } from './i18n';
import type { SavedNoticeReminder } from './types';

export default function AlertsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const {
    savedNoticeReminders,
    selectedLanguage,
    removeNoticeReminder,
    toggleNoticeReminderDone,
  } = useAppContext();

  const todayKey = formatDateKey(new Date());
  const sortedReminders = [...savedNoticeReminders].sort((a, b) => {
    if (a.isDone !== b.isDone) return a.isDone ? 1 : -1;
    if (a.dueDate !== b.dueDate) return a.dueDate.localeCompare(b.dueDate);
    return a.title.localeCompare(b.title);
  });

  const activeCount = savedNoticeReminders.filter((item) => !item.isDone).length;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={[styles.content, { paddingTop: insets.top + 18 }]}
    >
      <View style={styles.header}>
        <Text style={styles.screenTitle}>
          {selectedLanguage === 'Korean' ? '저장한 마감 알람' : 'Saved Deadline Alerts'}
        </Text>
        <Text style={styles.screenSubtitle}>
          {selectedLanguage === 'Korean'
            ? `저장한 마감일 ${savedNoticeReminders.length}개 중 ${activeCount}개가 남아 있습니다.`
            : `${activeCount} of ${savedNoticeReminders.length} saved deadlines remaining.`}
        </Text>
      </View>

      {sortedReminders.length > 0 ? (
        sortedReminders.map((reminder) => (
          <ReminderCard
            key={reminder.id}
            reminder={reminder}
            todayKey={todayKey}
            onPress={() =>
              router.push({ pathname: '/notices/[id]', params: { id: reminder.noticeId } })
            }
            onToggleDone={() => toggleNoticeReminderDone(reminder.id)}
            onRemove={() => removeNoticeReminder(reminder.noticeId)}
          />
        ))
      ) : (
        <View style={styles.emptyCard}>
          <Ionicons name="notifications-outline" size={36} color="#94A3B8" />
          <Text style={styles.emptyTitle}>
            {selectedLanguage === 'Korean' ? '저장한 알람이 없습니다' : 'No saved alerts'}
          </Text>
          <Text style={styles.emptyText}>
            {selectedLanguage === 'Korean'
              ? '공지 상세에서 마감일을 저장하면 이곳에 모아볼 수 있습니다.'
              : 'Save a deadline from a notice detail page to see it here.'}
          </Text>
        </View>
      )}
    </ScrollView>
  );
}

function ReminderCard({
  reminder,
  todayKey,
  onPress,
  onToggleDone,
  onRemove,
}: {
  reminder: SavedNoticeReminder;
  todayKey: string;
  onPress: () => void;
  onToggleDone: () => void;
  onRemove: () => void;
}) {
  const { selectedLanguage } = useAppContext();
  const isOverdue = !reminder.isDone && reminder.dueDate < todayKey;
  const isToday = !reminder.isDone && reminder.dueDate === todayKey;

  return (
    <View
      style={[
        styles.card,
        isToday && styles.todayCard,
        isOverdue && styles.overdueCard,
        reminder.isDone && styles.doneCard,
      ]}
    >
      <TouchableOpacity onPress={onPress} activeOpacity={0.85}>
        <View style={styles.cardTopRow}>
          <Text style={styles.category}>
            {getCategoryLabel(selectedLanguage, reminder.category)}
          </Text>

          <View style={styles.badgeRow}>
            {isOverdue ? (
              <View style={styles.overdueBadge}>
                <Text style={styles.overdueBadgeText}>
                  {selectedLanguage === 'Korean' ? '마감 지남' : 'Overdue'}
                </Text>
              </View>
            ) : null}
            {isToday ? (
              <View style={styles.todayBadge}>
                <Text style={styles.todayBadgeText}>
                  {selectedLanguage === 'Korean' ? '오늘 마감' : 'Due today'}
                </Text>
              </View>
            ) : null}
            {reminder.isDone ? (
              <View style={styles.doneBadge}>
                <Text style={styles.doneBadgeText}>
                  {selectedLanguage === 'Korean' ? '완료' : 'Done'}
                </Text>
              </View>
            ) : null}
          </View>
        </View>

        <Text style={[styles.cardTitle, reminder.isDone && styles.doneText]}>
          {reminder.title}
        </Text>
        <Text style={styles.cardSummary} numberOfLines={2}>
          {reminder.summary}
        </Text>
        <Text style={styles.cardDate}>
          {t(selectedLanguage, 'notices.deadline')} {reminder.dueDate}
        </Text>
      </TouchableOpacity>

      <View style={styles.actionRow}>
        <TouchableOpacity
          style={styles.iconButton}
          onPress={onToggleDone}
          activeOpacity={0.85}
        >
          <Ionicons
            name={reminder.isDone ? 'checkmark-circle' : 'ellipse-outline'}
            size={22}
            color={reminder.isDone ? '#38BDF8' : '#64748B'}
          />
          <Text style={styles.iconButtonText}>
            {reminder.isDone
              ? selectedLanguage === 'Korean'
                ? '완료됨'
                : 'Done'
              : selectedLanguage === 'Korean'
                ? '완료 표시'
                : 'Mark done'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.removeButton}
          onPress={onRemove}
          activeOpacity={0.85}
        >
          <Ionicons name="trash-outline" size={20} color="#B91C1C" />
          <Text style={styles.removeButtonText}>
            {selectedLanguage === 'Korean' ? '제거' : 'Remove'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

function formatDateKey(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F4F7FB',
  },
  content: {
    padding: 16,
    paddingBottom: 40,
  },
  header: {
    marginBottom: 18,
  },
  screenTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 6,
  },
  screenSubtitle: {
    fontSize: 14,
    color: '#64748B',
    lineHeight: 21,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  todayCard: {
    borderColor: '#F3D76B',
    backgroundColor: '#FFFBEA',
  },
  overdueCard: {
    borderColor: '#FDBA74',
    backgroundColor: '#FFF7ED',
  },
  doneCard: {
    backgroundColor: '#F8FAFC',
  },
  cardTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
    gap: 10,
  },
  category: {
    fontSize: 12,
    fontWeight: '800',
    color: '#005BAC',
  },
  badgeRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'flex-end',
    gap: 6,
    flex: 1,
  },
  todayBadge: {
    backgroundColor: '#FEF3C7',
    borderRadius: 999,
    paddingVertical: 4,
    paddingHorizontal: 9,
  },
  todayBadgeText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#92400E',
  },
  overdueBadge: {
    backgroundColor: '#FFEDD5',
    borderRadius: 999,
    paddingVertical: 4,
    paddingHorizontal: 9,
  },
  overdueBadgeText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#C2410C',
  },
  doneBadge: {
    backgroundColor: '#E0F7FF',
    borderRadius: 999,
    paddingVertical: 4,
    paddingHorizontal: 9,
  },
  doneBadgeText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#0284C7',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
    lineHeight: 23,
    marginBottom: 6,
  },
  doneText: {
    color: '#64748B',
  },
  cardSummary: {
    fontSize: 14,
    color: '#475569',
    lineHeight: 21,
    marginBottom: 10,
  },
  cardDate: {
    fontSize: 13,
    color: '#64748B',
    fontWeight: '700',
  },
  actionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 10,
    marginTop: 14,
  },
  iconButton: {
    flex: 1,
    minHeight: 42,
    borderRadius: 10,
    backgroundColor: '#EEF2F7',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
  },
  iconButtonText: {
    fontSize: 13,
    fontWeight: '800',
    color: '#334155',
  },
  removeButton: {
    minHeight: 42,
    borderRadius: 10,
    backgroundColor: '#FEF2F2',
    paddingHorizontal: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
  },
  removeButtonText: {
    fontSize: 13,
    fontWeight: '800',
    color: '#B91C1C',
  },
  emptyCard: {
    minHeight: 220,
    borderRadius: 14,
    backgroundColor: '#FFFFFF',
    padding: 22,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyTitle: {
    marginTop: 12,
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  emptyText: {
    marginTop: 8,
    fontSize: 14,
    color: '#64748B',
    lineHeight: 21,
    textAlign: 'center',
  },
});
