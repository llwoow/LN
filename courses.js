// 仅注册已有真实材料的课程。每门课程由章节生成图谱，也可提供经正文核对的知识联系。
window.LN_COURSES = Object.freeze([
  { ...window.LN_ELECTRICAL_MACHINES, knowledgeMap: window.LN_ELECTRICAL_MACHINES_MAP, workedExercises: ['transformer-homework', 'dc-homework-review'] },
  { ...window.LN_ELECTRICAL_MATERIALS, knowledgeMap: window.LN_ELECTRICAL_MATERIALS_MAP, workedExercises: ['em-test-summary', 'em-test-fill', 'em-test-short', 'em-test-review'] },
  { ...window.LN_NEW_ENERGY_MATERIALS, knowledgeMap: window.LN_NEW_ENERGY_MATERIALS_MAP, workedExercises: ['nem-homework'] },
  { ...window.LN_ELECTROMAGNETIC_COMPATIBILITY, knowledgeMap: window.LN_ELECTROMAGNETIC_COMPATIBILITY_MAP },
  { ...window.LN_DIGITAL_SIGNAL_PROCESSING, knowledgeMap: window.LN_DIGITAL_SIGNAL_PROCESSING_MAP },
  { ...window.LN_AUTO_CONTROL, knowledgeMap: window.LN_AUTO_CONTROL_MAP, workedExercises: ['ac-homework3', 'ac-homework4'] },
  { ...window.LN_ROBOT_DRIVE, knowledgeMap: window.LN_ROBOT_DRIVE_MAP },
  { ...window.LN_ENGLISH, knowledgeMap: window.LN_ENGLISH_MAP },
  { ...window.LN_POWER_SEMICONDUCTORS, workedExercises: ['chapter-2-test'] },
  ...(window.LN_HIGH_SCHOOL_COURSES || [])
].map(course => Object.freeze({
  ...course,
  libraryGroup: ({
    'electrical-machines': '电气工程',
    'electromagnetic-compatibility': '电气工程',
    'power-semiconductors': '电子与嵌入式',
    'robot-drive-engineering': '电子与嵌入式',
    'automatic-control': '控制与信号',
    'digital-signal-processing': '控制与信号',
    'electrical-materials': '材料与能源',
    'new-energy-materials': '材料与能源',
    'english': '通用能力'
  })[course.id] || (course.level === 'highschool' ? course.track : course.category)
})));
