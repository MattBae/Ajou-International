import Ionicons from '@expo/vector-icons/Ionicons';
import { StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

export default function ChatScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.botRow}>
        <View style={styles.botAvatar}>
          <Text style={styles.botEmoji}>A</Text>
        </View>

        <View style={styles.botBubble}>
          <Text style={styles.botText}>
            안녕하세요! 저는 아주대학교 유학생을 돕는 아잔입니다.
            오늘은 무엇을 도와드릴까요?
          </Text>
          <Text style={styles.timeText}>방금</Text>
        </View>
      </View>

      <View style={styles.quickColumn}>
        <TouchableOpacity style={styles.quickWideButton}>
          <Ionicons name="document-text-outline" size={18} color="#5B6FB8" />
          <Text style={styles.quickWideText}>비자 연장 절차</Text>
          <Ionicons name="chevron-forward" size={18} color="#5B6FB8" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.quickWideButton}>
          <Ionicons name="calendar-outline" size={18} color="#5B6FB8" />
          <Text style={styles.quickWideText}>학사 일정</Text>
          <Ionicons name="chevron-forward" size={18} color="#5B6FB8" />
        </TouchableOpacity>
      </View>

      <Text style={styles.topicTitle}>자주 찾는 주제</Text>

      <View style={styles.topicGrid}>
        <TouchableOpacity style={styles.topicButton}>
          <Ionicons name="card-outline" size={18} color="#5B6FB8" />
          <Text style={styles.topicText}>비자 신청</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.topicButton}>
          <Ionicons name="school-outline" size={18} color="#5B6FB8" />
          <Text style={styles.topicText}>TOPIK 시험</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.topicButton}>
          <Ionicons name="reader-outline" size={18} color="#5B6FB8" />
          <Text style={styles.topicText}>수강신청</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.topicButton}>
          <Ionicons name="briefcase-outline" size={18} color="#5B6FB8" />
          <Text style={styles.topicText}>아르바이트</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.inputBar}>
        <TouchableOpacity style={styles.smileButton}>
          <Ionicons name="happy-outline" size={22} color="#7C88B6" />
        </TouchableOpacity>

        <TextInput
          placeholder="질문을 입력하세요..."
          placeholderTextColor="#98A2B3"
          style={styles.input}
        />

        <TouchableOpacity style={styles.sendCircle}>
          <Ionicons name="send" size={18} color="#FFFFFF" />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F4F6FB',
    padding: 16,
    justifyContent: 'space-between',
  },
  botRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginTop: 8,
  },
  botAvatar: {
    width: 54,
    height: 54,
    borderRadius: 18,
    backgroundColor: '#E8EEFF',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  botEmoji: {
    fontSize: 26,
    fontWeight: '700',
    color: '#44528A',
  },
  botBubble: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 22,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  botText: {
    fontSize: 17,
    lineHeight: 28,
    color: '#3E4563',
  },
  timeText: {
    marginTop: 10,
    fontSize: 13,
    color: '#9AA3BF',
  },
  quickColumn: {
    marginTop: 14,
  },
  quickWideButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EEF2FF',
    borderRadius: 18,
    paddingVertical: 16,
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  quickWideText: {
    flex: 1,
    fontSize: 16,
    color: '#44528A',
    fontWeight: '600',
    marginLeft: 10,
  },
  topicTitle: {
    fontSize: 18,
    color: '#6B7390',
    marginTop: 10,
    marginBottom: 14,
  },
  topicGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  topicButton: {
    width: '48%',
    backgroundColor: '#F7F8FF',
    borderWidth: 1,
    borderColor: '#D9E1FF',
    borderRadius: 18,
    paddingVertical: 18,
    paddingHorizontal: 14,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  topicText: {
    marginLeft: 8,
    fontSize: 15,
    color: '#4C5678',
    fontWeight: '600',
    flexShrink: 1,
  },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8F7FF',
    borderTopWidth: 1,
    borderColor: '#E7E7F2',
    paddingTop: 14,
    paddingBottom: 6,
  },
  smileButton: {
    width: 42,
    height: 42,
    borderRadius: 21,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  input: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    paddingHorizontal: 18,
    paddingVertical: 12,
    fontSize: 16,
    color: '#334155',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  sendCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#7EA2FF',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 10,
  },
});
