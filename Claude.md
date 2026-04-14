# NewCore 補習班管理系統

## 專案架構
- 前端：GitHub Pages（index.html, admin.html）
- 後端：Google Apps Script（Code.gs）
- 通訊：JSONP（一般讀寫）/ fetch POST（大型資料）
- GAS網址：https://script.google.com/macros/s/AKfycbxE7aSryLEDxBqi-28EpdjvK9lhQwvGMKnWJlCbcHIG9Rc6FEPN3UrZwSIqMNVJ1GPs/exec

## Sheet 結構
- 授權中心 SheetID：1h3JG5HjMz0H4q8zXE7cFsLbfB-J63j6GjfudRkho1Jg
- 測試用客戶端 SheetID：1_25p98pfd3kS7bn8SbaDGRswv9ENIz-368brYWtr6OQ

## 重要規則
- GAS 每次修改後必須重新部署（New version）才會生效
- JSONP 用於一般讀寫，fetch POST 用於音訊、批次成績、建班
- 班級清單排除：規格、假日、系統設定、學生名單、Main、CHART_TEMP、成績單製作區、授權紀錄
- 班級清單按字母排序（.sort()）

## 權限架構
- superadmin：登入授權中心驗證（verifyMasterAuth），可操作所有補習班
- admin：登入授權中心驗證，只能操作 D欄指定的補習班
- teacher：登入客戶端 Sheet 驗證（verifyAuth），只能用 index.html

## GAS Actions 清單
### PUBLIC_ROUTES
- getClassList, getAvailableDates, getClassDataByCol
- getClassSummary, getGeminiKey, getStudentReport
- getClassStudents, getExamData, getSummaryStructure
- getTeacherList, getTeacherOverview
- verifyAuth, verifyMasterAuth
- getMyClasses, ping, clearCache
- getAvailableSpecs, getPreviewSchedule
- getMasterClients, getTeachers

### AUTH_ROUTES
- writeAttendance, writeCell, processVoice
- saveParentEmail, sendReportEmail
- saveExamScores, writeSummaryCells
- processSummaryVoice
- createClassSheet
- saveTeacher, deleteTeacher

## 已完成功能
- ✅ index.html：點名、總表、成績單、考試成績
- ✅ admin.html：建班（含假日跳過、單元對應）、老師管理
- ✅ 授權中心驗證（verifyMasterAuth）
- ✅ 多補習班切換（getMasterClients）

## 待完成功能
- 🚧 admin.html：學生名單 UI（從名單選取 + 手動輸入）
- 🚧 假日管理 UI
- 🚧 規格編輯 UI

## 學生名單分頁欄位
A：所屬班級　B：中文姓名　C：英文姓名
D：學校年級　E：電話　　　F：備註（家長Email）
第2列起為學生資料

## 出席符號
V=到　○=缺席　●=補課缺席　△=請假　▲=補課請假　⊝=遲到

## Gemini API
- Key：AIzaSyC5t7j79TGc4fuNhwMO1yA_oWWV0_ISBNE
- 模型：gemini-2.5-flash
- Key 從 GAS 的 getGeminiKey action 動態載入

## 注意事項
- GAS 改完永遠要重新部署 New version
- 前端呼叫 GAS 用 callGAS()（JSONP）或 postGAS()（POST）
- superadmin 不需要填 SheetId，自動看到全部補習班
- admin 需要在授權中心 D欄填入可操作的 SheetId
