// 仅注册已有真实材料的课程。每门课程由章节生成图谱，也可提供经正文核对的知识联系。
window.LN_COURSES = Object.freeze([
  { ...window.LN_ELECTRICAL_MACHINES, knowledgeMap: window.LN_ELECTRICAL_MACHINES_MAP },
  { ...window.LN_ELECTROMAGNETIC_COMPATIBILITY, knowledgeMap: window.LN_ELECTROMAGNETIC_COMPATIBILITY_MAP },
  { ...window.LN_AUTO_CONTROL, knowledgeMap: window.LN_AUTO_CONTROL_MAP },
  { ...window.LN_ROBOT_DRIVE, knowledgeMap: window.LN_ROBOT_DRIVE_MAP },
  window.LN_POWER_SEMICONDUCTORS,
  ...(window.LN_HIGH_SCHOOL_COURSES || [])
]);
