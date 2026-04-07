import { useState } from 'react';
import {
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from 'react-native';
import { useAppContext } from '../context/AppContext';
import type {
    AcademicStatus,
    LanguageOption,
    NoticeCategory,
    ResidenceType,
    StudentType,
    UserProfileStatus,
} from '../types';

export default function ProfileScreen() {
  const { userProfileStatus, setUserProfileStatus, setSelectedLanguage } =
    useAppContext();

  const [step, setStep] = useState<1 | 2>(1);
  const [form, setForm] = useState<UserProfileStatus>(userProfileStatus);

  const studentTypeOptions: StudentType[] = [
    'Undergraduate',
    'Graduate',
    'Exchange / Visiting',
  ];
  const academicStatusOptions: AcademicStatus[] = [
    'Enrolled',
    'On Leave',
    'Completed Coursework',
  ];
  const residenceOptions: ResidenceType[] = ['Dormitory', 'Off-campus'];
  const languageOptions: LanguageOption[] = ['English', 'Korean'];
  const interestOptions: NoticeCategory[] = [
    'Visa',
    'TOPIK',
    'Academic',
    'Events',
    'Scholarship',
    'Dormitory',
  ];

  const updateField = <K extends keyof UserProfileStatus>(
    key: K,
    value: UserProfileStatus[K]
  ) => {
    setForm((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const toggleInterest = (category: NoticeCategory) => {
    setForm((prev) => {
      const exists = prev.interests.includes(category);

      return {
        ...prev,
        interests: exists
          ? prev.interests.filter((item) => item !== category)
          : [...prev.interests, category],
      };
    });
  };

  const handleSave = () => {
    setUserProfileStatus(form);
    setSelectedLanguage(form.preferredLanguage);
  };

  const renderOptionButtons = <T extends string>(
    options: T[],
    selectedValue: T,
    onSelect: (value: T) => void
  ) => {
    return (
      <View style={styles.optionGroup}>
        {options.map((option) => {
          const isSelected = selectedValue === option;

          return (
            <TouchableOpacity
              key={option}
              style={[
                styles.optionButton,
                isSelected && styles.optionButtonSelected,
              ]}
              onPress={() => onSelect(option)}
              activeOpacity={0.85}
            >
              <Text
                style={[
                  styles.optionButtonText,
                  isSelected && styles.optionButtonTextSelected,
                ]}
              >
                {option === 'English'
                  ? '영어'
                  : option === 'Korean'
                    ? '한국어'
                    : option}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.headerTitle}>내 프로필</Text>
      <Text style={styles.headerSubtitle}>
        학적 정보, 비자 정보, 개인화 설정을 수정해보세요
      </Text>

      <View style={styles.stepRow}>
        <TouchableOpacity
          style={[styles.stepButton, step === 1 && styles.activeStepButton]}
          onPress={() => setStep(1)}
          activeOpacity={0.85}
        >
          <Text
            style={[styles.stepText, step === 1 && styles.activeStepText]}
          >
            1단계
          </Text>
          <Text
            style={[
              styles.stepSubText,
              step === 1 && styles.activeStepSubText,
            ]}
          >
            계정 및 학적
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.stepButton, step === 2 && styles.activeStepButton]}
          onPress={() => setStep(2)}
          activeOpacity={0.85}
        >
          <Text
            style={[styles.stepText, step === 2 && styles.activeStepText]}
          >
            2단계
          </Text>
          <Text
            style={[
              styles.stepSubText,
              step === 2 && styles.activeStepSubText,
            ]}
          >
            비자 및 개인화
          </Text>
        </TouchableOpacity>
      </View>

      {step === 1 && (
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>계정 및 학적 정보</Text>

          <View style={styles.field}>
            <Text style={styles.label}>학교 이메일</Text>
            <TextInput
              value={form.schoolEmail}
              onChangeText={(text) => updateField('schoolEmail', text)}
              style={styles.input}
              placeholder="student@ajou.ac.kr"
              placeholderTextColor="#94A3B8"
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>학생 유형</Text>
            {renderOptionButtons(studentTypeOptions, form.studentType, (value) =>
              updateField('studentType', value)
            )}
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>학적 상태</Text>
            {renderOptionButtons(
              academicStatusOptions,
              form.academicStatus,
              (value) => updateField('academicStatus', value)
            )}
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>학년</Text>
            <TextInput
              value={form.year}
              onChangeText={(text) => updateField('year', text)}
              style={styles.input}
              placeholder="3"
              placeholderTextColor="#94A3B8"
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>학기</Text>
            <TextInput
              value={form.semester}
              onChangeText={(text) => updateField('semester', text)}
              style={styles.input}
              placeholder="1"
              placeholderTextColor="#94A3B8"
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>학번</Text>
            <TextInput
              value={form.studentId}
              onChangeText={(text) => updateField('studentId', text)}
              style={styles.input}
              placeholder="2022xxxx"
              placeholderTextColor="#94A3B8"
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>전공</Text>
            <TextInput
              value={form.major}
              onChangeText={(text) => updateField('major', text)}
              style={styles.input}
              placeholder="Digital Media"
              placeholderTextColor="#94A3B8"
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>평점</Text>
            <TextInput
              value={form.gpa}
              onChangeText={(text) => updateField('gpa', text)}
              style={styles.input}
              placeholder="3.50"
              placeholderTextColor="#94A3B8"
            />
          </View>

          <TouchableOpacity
            style={styles.nextButton}
            onPress={() => setStep(2)}
            activeOpacity={0.85}
          >
            <Text style={styles.nextButtonText}>다음 단계</Text>
          </TouchableOpacity>
        </View>
      )}

      {step === 2 && (
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>비자 및 개인화 설정</Text>

          <View style={styles.field}>
            <Text style={styles.label}>비자 유형</Text>
            <TextInput
              value={form.visaType}
              onChangeText={(text) => updateField('visaType', text)}
              style={styles.input}
              placeholder="D-2"
              placeholderTextColor="#94A3B8"
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>선호 언어</Text>
            {renderOptionButtons(languageOptions, form.preferredLanguage, (value) =>
              updateField('preferredLanguage', value)
            )}
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>거주 형태</Text>
            {renderOptionButtons(residenceOptions, form.residenceType, (value) =>
              updateField('residenceType', value)
            )}
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>TOPIK 상태</Text>
            <TextInput
              value={form.topikStatus}
              onChangeText={(text) => updateField('topikStatus', text)}
              style={styles.input}
              placeholder="TOPIK Level 4"
              placeholderTextColor="#94A3B8"
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>관심 카테고리</Text>
            <View style={styles.interestWrap}>
              {interestOptions.map((category) => {
                const isSelected = form.interests.includes(category);

                return (
                  <TouchableOpacity
                    key={category}
                    style={[
                      styles.interestChip,
                      isSelected && styles.interestChipSelected,
                    ]}
                    onPress={() => toggleInterest(category)}
                    activeOpacity={0.85}
                  >
                    <Text
                      style={[
                        styles.interestChipText,
                        isSelected && styles.interestChipTextSelected,
                      ]}
                    >
                      {category}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>
          </View>

          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => setStep(1)}
              activeOpacity={0.85}
            >
              <Text style={styles.secondaryButtonText}>이전</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.primaryButton}
              onPress={handleSave}
              activeOpacity={0.85}
            >
              <Text style={styles.primaryButtonText}>프로필 저장</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F4F7FB',
  },
  content: {
    padding: 16,
    paddingBottom: 28,
  },
  headerTitle: {
    fontSize: 26,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 6,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#64748B',
    lineHeight: 20,
    marginBottom: 20,
  },
  stepRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 18,
  },
  stepButton: {
    flex: 1,
    backgroundColor: '#E2E8F0',
    borderRadius: 14,
    paddingVertical: 14,
    paddingHorizontal: 12,
  },
  activeStepButton: {
    backgroundColor: '#D95C4F',
  },
  stepText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 4,
  },
  activeStepText: {
    color: '#FFFFFF',
  },
  stepSubText: {
    fontSize: 12,
    color: '#475569',
  },
  activeStepSubText: {
    color: '#FFF7F5',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 16,
  },
  field: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0F172A',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 13,
    fontSize: 14,
    color: '#0F172A',
  },
  optionGroup: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  optionButton: {
    backgroundColor: '#F1F5F9',
    borderRadius: 999,
    paddingVertical: 10,
    paddingHorizontal: 14,
  },
  optionButtonSelected: {
    backgroundColor: '#FFF1EE',
    borderWidth: 1,
    borderColor: '#F4B4AC',
  },
  optionButtonText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#475569',
  },
  optionButtonTextSelected: {
    color: '#D95C4F',
  },
  interestWrap: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  interestChip: {
    backgroundColor: '#F1F5F9',
    borderRadius: 999,
    paddingVertical: 10,
    paddingHorizontal: 14,
  },
  interestChipSelected: {
    backgroundColor: '#FFF1EE',
    borderWidth: 1,
    borderColor: '#F4B4AC',
  },
  interestChipText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#475569',
  },
  interestChipTextSelected: {
    color: '#D95C4F',
  },
  nextButton: {
    backgroundColor: '#D95C4F',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 4,
  },
  nextButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 8,
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: '#E2E8F0',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
  },
  secondaryButtonText: {
    color: '#334155',
    fontSize: 15,
    fontWeight: '700',
  },
  primaryButton: {
    flex: 1,
    backgroundColor: '#D95C4F',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
  },
});
