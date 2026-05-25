export type InformationMenuKey =
  | 'visa'
  | 'topik'
  | 'register'
  | 'scholarship'
  | 'life';

export type InformationMenuPart = {
  menuKey: InformationMenuKey;
  menuTitle: string;
  partKey: string;
  partTitle: string;
  sectionTitle: string;
  content: string;
  sourceUrl?: string;
};

export const INFORMATION_MENU_PARTS: InformationMenuPart[] = [
  {
    menuKey: 'visa',
    menuTitle: '비자',
    partKey: 'overview',
    partTitle: '개요',
    sectionTitle: 'D-2 유학 체류자격 개요',
    content:
      'D-2는 정규 대학 과정에 재학하는 외국인을 위한 유학 체류자격입니다. 체류기간은 보통 1~2년 단위로 발급되며, 재학 중에는 만료 전에 연장 신청을 완료해야 합니다.',
  },
  {
    menuKey: 'visa',
    menuTitle: '비자',
    partKey: 'extension',
    partTitle: '연장',
    sectionTitle: '체류기간 연장',
    content:
      '비자 만료 전에 하이코리아 또는 관할 출입국사무소에서 체류기간 연장을 신청합니다. 여권, 외국인등록증, 신청서, 재학증명서, 등록금 납입증명서, 성적증명서, 체류지 증빙, 수수료 등을 준비합니다.',
    sourceUrl: 'https://www.hikorea.go.kr',
  },
  {
    menuKey: 'visa',
    menuTitle: '비자',
    partKey: 'change',
    partTitle: '변경',
    sectionTitle: '체류자격 변경',
    content:
      '어학연수 D-4에서 학위과정 D-2로 변경하거나 졸업 후 연구 체류자격으로 변경할 때에는 학기 시작 전 관할 출입국사무소에 체류자격 변경허가를 신청해야 합니다.',
    sourceUrl: 'https://www.hikorea.go.kr',
  },
  {
    menuKey: 'visa',
    menuTitle: '비자',
    partKey: 'work',
    partTitle: '시간제취업',
    sectionTitle: '시간제취업 허가',
    content:
      '유학생이 시간제취업을 하려면 근무 시작 전에 허가를 받아야 합니다. 하이코리아 전자민원에서 유학생 시간제취업 허가를 신청하고, 고용계약서와 학교 확인 서류 등을 제출합니다.',
    sourceUrl: 'https://www.hikorea.go.kr',
  },
  {
    menuKey: 'visa',
    menuTitle: '비자',
    partKey: 'links',
    partTitle: '공식 링크',
    sectionTitle: '비자 공식 링크',
    content:
      '비자 신청, 체류기간 연장, 체류자격 변경, 시간제취업 허가 등 출입국 관련 민원은 하이코리아 공식 사이트에서 확인합니다.',
    sourceUrl: 'https://www.hikorea.go.kr',
  },
  {
    menuKey: 'topik',
    menuTitle: 'TOPIK',
    partKey: 'pbt',
    partTitle: 'PBT',
    sectionTitle: 'TOPIK PBT',
    content:
      'TOPIK PBT는 종이 기반 한국어능력시험입니다. 시험 접수기간, 수험표 출력기간, 시험일, 성적 발표일을 확인하고 신분증과 수험표를 준비해야 합니다.',
    sourceUrl: 'https://www.topik.go.kr',
  },
  {
    menuKey: 'topik',
    menuTitle: 'TOPIK',
    partKey: 'ibt',
    partTitle: 'IBT',
    sectionTitle: 'TOPIK IBT',
    content:
      'TOPIK IBT는 컴퓨터 기반 한국어능력시험입니다. 시험장 컴퓨터로 응시하며 PBT와 동일한 등급체계를 사용합니다. 접수기간과 시험장 공지를 반드시 확인합니다.',
    sourceUrl: 'https://www.topik.go.kr',
  },
  {
    menuKey: 'topik',
    menuTitle: 'TOPIK',
    partKey: 'speaking',
    partTitle: '말하기 평가',
    sectionTitle: 'TOPIK 말하기 평가',
    content:
      'TOPIK 말하기 평가는 한국어 말하기 능력을 평가하는 시험입니다. 응시자는 입실 시간, 준비물, 신분증 규정, 성적 발표일을 사전에 확인해야 합니다.',
    sourceUrl: 'https://www.topik.go.kr',
  },
  {
    menuKey: 'register',
    menuTitle: '입학 등록',
    partKey: 'steps',
    partTitle: '지원절차',
    sectionTitle: '한국어과정 지원절차',
    content:
      '한국어과정 지원은 온라인 지원, 계정 생성, 지원서 작성 및 제출, 심사와 합격 통보, 학비 납부, 표준입학허가서 발급, 비자 신청, 레벨테스트, 입학 순서로 진행됩니다.',
  },
  {
    menuKey: 'register',
    menuTitle: '입학 등록',
    partKey: 'info',
    partTitle: '지원정보',
    sectionTitle: '한국어과정 지원정보',
    content:
      '한국어과정 지원자는 신청기간, 지원자격, 학비, 보험, 추가 안내사항을 확인해야 합니다. 학기별 신청기간과 개강일은 학사일정에 따라 달라질 수 있습니다.',
  },
  {
    menuKey: 'register',
    menuTitle: '입학 등록',
    partKey: 'documents',
    partTitle: '비자/서류',
    sectionTitle: '한국어과정 제출서류',
    content:
      'D-4 비자 신청자는 입학신청서, 최종학력 증명서, 성적증명서, 재정증명, 가족관계 증명, 여권 사본 등 필요한 서류를 준비해야 합니다. 국가와 체류상태에 따라 추가 서류가 필요할 수 있습니다.',
  },
  {
    menuKey: 'register',
    menuTitle: '입학 등록',
    partKey: 'schedule',
    partTitle: '학사일정',
    sectionTitle: '한국어과정 학사일정',
    content:
      '한국어과정은 봄, 여름, 가을, 겨울 학기로 운영됩니다. 각 학기는 신청기간, 레벨테스트, 신입생 설명회, 개강일, 수료일이 정해져 있으므로 본인의 목표 학기를 확인해야 합니다.',
  },
  {
    menuKey: 'scholarship',
    menuTitle: '장학금',
    partKey: 'korean',
    partTitle: '한국어과정',
    sectionTitle: '한국어과정 장학',
    content:
      '한국어과정 장학에는 신입생 장학, 아주 가족 장학, SDG 장학 등이 있습니다. 장학 조건은 입학성적, 가족 재학 여부, 사회적 배려 필요성 등에 따라 달라질 수 있습니다.',
    sourceUrl: 'https://cie.ajou.ac.kr/cie/korean/scholarship.do',
  },
  {
    menuKey: 'scholarship',
    menuTitle: '장학금',
    partKey: 'gks',
    partTitle: 'GKS',
    sectionTitle: 'GKS 정부초청장학',
    content:
      'GKS는 외국인 학생에게 대한민국 고등교육기관에서 수학할 기회를 제공하는 장학제도입니다. 한국어 연수와 학위과정, 생활비, 항공료 등 지원 내용과 선발일정을 확인해야 합니다.',
    sourceUrl: 'https://www.niied.go.kr',
  },
  {
    menuKey: 'scholarship',
    menuTitle: '장학금',
    partKey: 'achievement',
    partTitle: '성적/TOPIK',
    sectionTitle: '성적 및 TOPIK 장학',
    content:
      '성적 우수 장학과 TOPIK 장학은 학업성적 또는 TOPIK 취득 급수에 따라 수강료 감면이나 응시료 지원을 받을 수 있는 제도입니다.',
  },
  {
    menuKey: 'scholarship',
    menuTitle: '장학금',
    partKey: 'etc',
    partTitle: '기타',
    sectionTitle: '기타 장학',
    content:
      '기타 장학에는 GKS 관련 장학, 근로장학, 반장장학 등이 포함됩니다. 세부 조건과 지급 방식은 공지와 센터 안내에 따라 확인합니다.',
  },
  {
    menuKey: 'life',
    menuTitle: '생활 정보',
    partKey: 'support',
    partTitle: '생활지원',
    sectionTitle: '외국인 학생 생활지원',
    content:
      '생활지원 정보에는 외국인등록증 신청, 체류기간 연장, 체류지 변경신고, 도서관 이용, 학생증, 보건진료소 이용 안내가 포함됩니다.',
  },
  {
    menuKey: 'life',
    menuTitle: '생활 정보',
    partKey: 'dorm',
    partTitle: '기숙사',
    sectionTitle: '기숙사 신청 및 생활',
    content:
      '기숙사 정보에는 신입생과 재학생 신청방법, 기숙사비, 납부기간, 입실 문의, 학교 및 기숙사 영상 링크가 포함됩니다. 기숙사 여석과 일정에 따라 입주 가능 여부가 달라질 수 있습니다.',
  },
];
