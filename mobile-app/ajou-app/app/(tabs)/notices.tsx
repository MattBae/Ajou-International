import { useRouter } from 'expo-router';
import { useState } from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useAppContext } from '../context/AppContext';
import type { NoticeCategory } from '../types';

export default function NoticesScreen() {
  const router = useRouter();
  const { notices, toggleNoticeReminder, savedNoticeReminders } = useAppContext();
  const [selectedCategory, setSelectedCategory] =
    useState<NoticeCategory | 'All'>('All');

  const categories: (NoticeCategory | 'All')[] = [
    'All',
    'Visa',
    'TOPIK',
    'Academic',
    'Events',
    'Scholarship',
    'Dormitory',
  ];

  const filteredNotices =
    selectedCategory === 'All'
      ? notices
      : notices.filter((notice) => notice.category === selectedCategory);

  const handlePressNotice = (id: string) => {
    router.push({ pathname: '/notices/[id]', params: { id } });
  };

  return (
    <View style={styles.container}>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.tabsContainer}
      >
        {categories.map((category) => {
          const isActive = selectedCategory === category;

          return (
            <TouchableOpacity
              key={category}
              style={[styles.tab, isActive && styles.activeTab]}
              onPress={() => setSelectedCategory(category)}
            >
              <Text style={[styles.tabText, isActive && styles.activeTabText]}>
                {category === 'All' ? '전체' : category}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      <ScrollView showsVerticalScrollIndicator={false}>
        {filteredNotices.map((notice) => {
          const isSaved = savedNoticeReminders.some(
            (item) => item.noticeId === notice.id
          );

          return (
            <View key={notice.id} style={styles.card}>
              <TouchableOpacity
                onPress={() => handlePressNotice(notice.id)}
                activeOpacity={0.8}
              >
                <View style={styles.cardTopRow}>
                  <Text style={styles.category}>{notice.category}</Text>
                  <View style={styles.badgeRow}>
                    {notice.hasAttachmentOnly ? (
                      <View style={styles.imageBadge}>
                        <Text style={styles.imageBadgeText}>이미지 첨부</Text>
                      </View>
                    ) : null}
                    {notice.isCritical && (
                      <View style={styles.badge}>
                        <Text style={styles.badgeText}>중요</Text>
                      </View>
                    )}
                  </View>
                </View>

                <Text style={styles.title}>{notice.title}</Text>
                <Text style={styles.summary} numberOfLines={3}>
                  {notice.summary}
                </Text>
                <Text style={styles.date}>
                  {notice.deadline ? `마감일 ${notice.deadline}` : `게시일 ${notice.date}`}
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.saveButton, isSaved && styles.savedButton]}
                onPress={() => toggleNoticeReminder(notice)}
                activeOpacity={0.85}
              >
                <Text style={styles.saveButtonText}>
                  {isSaved ? '캘린더에서 제거' : '마감일 저장'}
                </Text>
              </TouchableOpacity>
            </View>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#F4F7FB',
  },
  tabsContainer: {
    paddingBottom: 12,
  },
  tab: {
    backgroundColor: '#E2E8F0',
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 20,
    marginRight: 8,
  },
  activeTab: {
    backgroundColor: '#D95C4F',
  },
  tabText: {
    color: '#334155',
    fontSize: 14,
  },
  activeTabText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
    minHeight: 168,
  },
  cardTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  category: {
    fontSize: 12,
    fontWeight: '600',
    color: '#D95C4F',
  },
  badge: {
    backgroundColor: '#FEE2E2',
    borderRadius: 999,
    paddingVertical: 4,
    paddingHorizontal: 10,
  },
  badgeText: {
    fontSize: 11,
    color: '#B91C1C',
    fontWeight: '600',
  },
  imageBadge: {
    backgroundColor: '#DBEAFE',
    borderRadius: 999,
    paddingVertical: 4,
    paddingHorizontal: 10,
  },
  imageBadgeText: {
    fontSize: 11,
    color: '#1D4ED8',
    fontWeight: '600',
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 6,
  },
  summary: {
    fontSize: 14,
    color: '#475569',
    marginBottom: 10,
    lineHeight: 22,
    minHeight: 66,
  },
  date: {
    fontSize: 12,
    color: '#94A3B8',
  },
  saveButton: {
    marginTop: 12,
    backgroundColor: '#D95C4F',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
  },
  savedButton: {
    backgroundColor: '#0F766E',
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
});
