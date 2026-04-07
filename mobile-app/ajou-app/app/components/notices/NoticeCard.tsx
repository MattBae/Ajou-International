import { StyleSheet, Text, View } from 'react-native';
import type { Notice } from '../../types';

type Props = {
  notice: Notice;
};

export default function NoticeCard({ notice }: Props) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{notice.title}</Text>
      <Text style={styles.meta}>
        Category: {notice.category} | Priority: {notice.isCritical ? 'High' : 'Normal'}
      </Text>
      <Text style={styles.deadline}>Date: {notice.date}</Text>
      <Text style={styles.body}>{notice.description ?? notice.summary}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 18,
    marginBottom: 14,
  },
  title: {
    fontSize: 17,
    fontWeight: '700',
    color: '#17324D',
    marginBottom: 8,
  },
  meta: {
    fontSize: 13,
    color: '#5C748C',
    marginBottom: 6,
  },
  deadline: {
    fontSize: 13,
    color: '#C0392B',
    marginBottom: 8,
  },
  body: {
    fontSize: 14,
    color: '#334E68',
    lineHeight: 21,
  },
});
