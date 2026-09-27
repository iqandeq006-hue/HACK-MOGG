/* ============================================================
   MOGG SkillSwap — Frontend App (API-Backed)
   All data operations call the FastAPI backend at /api/*
   ============================================================ */

const API = (window.location.protocol === 'file:' || (window.location.port && window.location.port !== '8000'))
  ? 'http://localhost:8000'
  : '';

/* ---------- STATE ---------- */
let currentUser = null;       // { id, name, email, bio, balance, escrow_balance, teach_listings, learn_listings }
let communitySkills = [];     // from /api/community/skills
let allUsers = [];            // from /api/users
let sessions = [];            // from /api/sessions?user_id=
let view = 'login';
let homeFilterTab = 'all';
let activeCatTab = 'all';
let searchQuery = '';
let sidebarPriceFilter = 'all';
let sidebarLevelFilter = 'all';
let mySkillsActiveTab = 'purchased';
let activeSkillDetailState = null;
let activePaymentMethod = 'mg';
let isPaymentModalOpen = false;
let chatMessages = [];
let activeChatSessionId = null;

let groupRooms = [];
let activeGroupRoomId = null;
let groupMessages = [];
let isCreateGroupModalOpen = false;
let isInviteGroupModalOpen = false;

let activeCommunityTab = 'channels'; // 'channels' | 'private'
let privateConversations = [];
let activeCourseModal = null;
let activeQuizAnswers = {};

let addSkillFormState = {
  id: null, type: 'teach', domain: 'tech', name: '', fee: '⚡ 1 Credit / Session', description: '', image: ''
};

let aiTutorHistory = [
  {
    role: 'assistant',
    content: "👋 Hi! I'm **SkillBot**, your peer learning mentor on MOGG. Ask me any conceptual doubt about programming, math, design, or public speaking, or ask for a **3-drill practice agenda** to prepare before your 1-on-1 peer session!"
  }
];
let aiTutorSkillContext = 'React';
let isAiTutorLoading = false;

// Domain Free Training & Certification Courses
const DOMAIN_COURSES = {
  tech: {
    domain: 'tech',
    title: 'Modern Fullstack & AI Agent Engineering',
    categoryLabel: 'Tech Skills',
    duration: '15 min crash course',
    summary: 'Master fullstack decoupled architecture, stateful REST APIs, and autonomous AI tool-calling loops with sentence embeddings for semantic search.',
    takeaways: [
      'Decoupled client-server design using pure REST boundaries',
      'Dense vector representations (384-dim MiniLM embeddings) for semantic matching',
      'Atomic escrow state machines preventing double spending'
    ],
    quiz: [
      {
        q: 'What is the primary advantage of Dense Vector Semantic Matching over traditional keyword matching?',
        options: [
          'It only matches exact character strings',
          'It connects conceptual synonyms (e.g. "React" with "Frontend Development") regardless of vocabulary differences',
          'It requires a paid external API to calculate similarity',
          'It slows down search queries by converting text into raw HTML'
        ],
        correct: 1
      },
      {
        q: 'Why does MOGG utilize a 4-state escrow FSM for credit exchanges?',
        options: [
          'To permanently burn coins from the system',
          'To lock credits during the session and protect peers against no-shows and flakes',
          'To convert MG coins into cryptocurrency tokens',
          'To force students to pay real money'
        ],
        correct: 1
      }
    ]
  },
  soft: {
    domain: 'soft',
    title: 'High-Impact Communication & Executive Pitching',
    categoryLabel: 'Soft Skills',
    duration: '12 min crash course',
    summary: 'Master active listening, vocal cadence, structured storytelling, and psychological safety in collaborative peer learning circles.',
    takeaways: [
      'Active listening: reflecting intent and paraphrasing before responding',
      'Structuring peer feedback using the SBI (Situation-Behavior-Impact) model',
      'Constructive conflict resolution and mutual goal alignment'
    ],
    quiz: [
      {
        q: 'In collaborative peer mentorship, what is the core tenet of Active Listening?',
        options: [
          'Waiting silently until it is your turn to speak',
          'Paraphrasing and verifying understanding of the peer’s perspective before offering advice',
          'Interrupting immediately when an error is detected',
          'Taking written notes without maintaining eye contact'
        ],
        correct: 1
      },
      {
        q: 'What is the best way to handle an agenda disagreement during a 1-on-1 swap?',
        options: [
          'Decline the session immediately and block the peer',
          'Align on mutual learning goals and split the time evenly using a shared agenda',
          'Insist on your topic exclusively',
          'Report the user to platform administrators'
        ],
        correct: 1
      }
    ]
  },
  survival: {
    domain: 'survival',
    title: 'Field Wilderness Survival & Emergency Readiness',
    categoryLabel: 'Survival Skills',
    duration: '14 min crash course',
    summary: 'Learn the core survival priorities: shelter building, friction fire craft, emergency water purification, and wilderness first response.',
    takeaways: [
      'The Rule of 3s: 3 minutes without air, 3 hours without shelter, 3 days without water',
      'Tarp tensioning knots and weather-resistant debris huts',
      'Field triage and emergency trauma stabilization'
    ],
    quiz: [
      {
        q: 'According to survival doctrine, what is the "Rule of 3s" priority hierarchy?',
        options: [
          '3 days without food, 3 weeks without shelter, 3 hours without water',
          '3 minutes without air, 3 hours without shelter in harsh cold, 3 days without water, 3 weeks without food',
          '3 miles of hiking per hour, 3 liters of water per day, 3 layers of clothing',
          '3 campfires per night, 3 whistles for help, 3 flares at dawn'
        ],
        correct: 1
      },
      {
        q: 'Which friction fire method utilizes a spindle, socket block, bow, and notched hearthboard?',
        options: [
          'Hand drill',
          'Bow drill',
          'Fire plow',
          'Flint and steel'
        ],
        correct: 1
      }
    ]
  },
  creative: {
    domain: 'creative',
    title: 'Digital UI/UX & Visual Design Systems',
    categoryLabel: 'Creative Skills',
    duration: '15 min crash course',
    summary: 'Master typographic scales, color contrast ratios (WCAG AAA), auto-layout component architectures, and responsive micro-interactions.',
    takeaways: [
      'Design tokens: centralized source of truth for colors, typography, and spacing',
      'Visual hierarchy: guiding user attention through contrast and whitespace',
      'Interactive prototyping and user usability testing'
    ],
    quiz: [
      {
        q: 'What is the primary function of Design Tokens in modern design systems?',
        options: [
          'Cryptographic assets used to pay designers',
          'Centralized, reusable key-value variables (colors, spacing, font sizes) shared across design and code',
          'Raster image assets exported at 1x resolution',
          'Watermarks placed over vector icons'
        ],
        correct: 1
      },
      {
        q: 'To meet WCAG AA standards, what is the minimum contrast ratio for normal body text against its background?',
        options: [
          '2:1',
          '4.5:1',
          '10:1',
          '1:1'
        ],
        correct: 1
      }
    ]
  },
  business: {
    domain: 'business',
    title: 'Lean Startup Strategy & Product Discovery',
    categoryLabel: 'Business Skills',
    duration: '15 min crash course',
    summary: 'Learn value proposition design, customer discovery interviews, unit economics, and rapid hypothesis validation without code.',
    takeaways: [
      'Formulating falsifiable hypotheses before writing code',
      'The Double Coincidence of Wants and network liquidity in marketplace design',
      'Unit economics: Customer Acquisition Cost (CAC) vs Lifetime Value (LTV)'
    ],
    quiz: [
      {
        q: 'What economic problem does MOGG’s Time-Banking Credit Ledger eliminate?',
        options: [
          'Inflation of fiat currencies',
          'The Double Coincidence of Wants (where User A teaches B, but B cannot teach A what A needs)',
          'High credit card transaction fees',
          'Supply chain shipping delays'
        ],
        correct: 1
      },
      {
        q: 'In Lean Startup methodology, what is the purpose of an MVP (Minimum Viable Product)?',
        options: [
          'To generate the maximum possible revenue on day one',
          'To maximize validated learning about customers with the least effort',
          'To replace the need for customer feedback',
          'To eliminate software testing'
        ],
        correct: 1
      }
    ]
  },
  languages: {
    domain: 'languages',
    title: 'Conversational Fluency & Language Immersion',
    categoryLabel: 'Language Skills',
    duration: '12 min crash course',
    summary: 'Master comprehensible input techniques, spaced repetition memory drills, and high-frequency conversational dialogue routines.',
    takeaways: [
      'Focusing on the top 500 high-frequency words for 75% of spoken comprehension',
      'Spaced repetition systems (SRS) for long-term retention',
      'Overcoming speaking inhibition through reciprocal tandem language exchange'
    ],
    quiz: [
      {
        q: 'In tandem language exchange between two peers, what is the gold standard practice for time division?',
        options: [
          'Speak only in the dominant peer’s native language',
          'Split session time 50/50 so both participants practice their target language with a native speaker',
          'Speak a third neutral language during the entire call',
          'Switch languages every 30 seconds'
        ],
        correct: 1
      },
      {
        q: 'What does Stephen Krashen’s "Comprehensible Input" theory emphasize for rapid acquisition?',
        options: [
          'Memorizing complete grammar dictionaries before speaking',
          'Consuming messages and dialogues that are just slightly above your current level (i+1) in natural context',
          'Strict silent reading for the first two years',
          'Taking multiple-choice grammar exams weekly'
        ],
        correct: 1
      }
    ]
  }
};

// Trending skills catalogue (static, matching MOGG-main)
const TRENDING_CATALOGUE = [
  { id: 'tech-1', category: 'tech', categoryLabel: 'Tech Skills', title: 'AI Prompt Engineering & Agents', difficulty: 'Intermediate', duration: '~1h 30m', description: 'Design autonomous AI agents, tool calling loops, and structured LLM prompts.', tags: ['AI', 'Python', 'LLMs'] },
  { id: 'tech-2', category: 'tech', categoryLabel: 'Tech Skills', title: 'Fullstack Web App with React & Vite', difficulty: 'Beginner', duration: '~2h 15m', description: 'Build fast client-side applications with modern component architectures.', tags: ['React', 'JavaScript', 'CSS'] },
  { id: 'tech-3', category: 'tech', categoryLabel: 'Tech Skills', title: 'Python for Data Science & ML', difficulty: 'Beginner', duration: '~1h 45m', description: 'Clean datasets, calculate statistics, and build basic prediction models.', tags: ['Python', 'Pandas', 'ML'] },
  { id: 'tech-4', category: 'tech', categoryLabel: 'Tech Skills', title: 'Cybersecurity & Network Defense', difficulty: 'Advanced', duration: '~2h 00m', description: 'Understand packet inspection, threat modeling, and intrusion detection.', tags: ['Cybersecurity', 'Networks', 'Linux'] },
  { id: 'soft-1', category: 'soft', categoryLabel: 'Soft Skills', title: 'Executive Public Speaking & Pitching', difficulty: 'Beginner', duration: '~45 min', description: 'Master body language, vocal pacing, and slide deck storytelling.', tags: ['Speaking', 'Communication', 'Pitching'] },
  { id: 'soft-2', category: 'soft', categoryLabel: 'Soft Skills', title: 'High-Stakes Negotiation & Persuasion', difficulty: 'Intermediate', duration: '~1h 10m', description: 'Learn win-win negotiation tactics, objection handling, and deal structuring.', tags: ['Negotiation', 'Business', 'Leadership'] },
  { id: 'soft-3', category: 'soft', categoryLabel: 'Soft Skills', title: 'Conflict Resolution & Team Coaching', difficulty: 'Intermediate', duration: '~50 min', description: 'Navigate team disagreements constructively and foster productive collaboration.', tags: ['Management', 'Empathy', 'Teams'] },
  { id: 'soft-4', category: 'soft', categoryLabel: 'Soft Skills', title: 'Emotional Intelligence & Stress Mastery', difficulty: 'Beginner', duration: '~40 min', description: 'Build self-awareness, active listening skills, and workplace resilience.', tags: ['Mindfulness', 'EQ', 'Growth'] },
  { id: 'surv-1', category: 'survival', categoryLabel: 'Survival Skills', title: 'Wilderness First Aid & Emergency CPR', difficulty: 'Intermediate', duration: '~1h 30m', description: 'Essential field triage, wound bandaging, fracture stabilization, and CPR.', tags: ['First Aid', 'Safety', 'Outdoors'] },
  { id: 'surv-2', category: 'survival', categoryLabel: 'Survival Skills', title: 'Emergency Shelter & Firemaking', difficulty: 'Beginner', duration: '~1h 00m', description: 'Friction fire starting, weather-resistant shelter construction, and knot tying.', tags: ['Bushcraft', 'Shelter', 'Fire'] },
  { id: 'surv-3', category: 'survival', categoryLabel: 'Survival Skills', title: 'Urban Navigation & Emergency Prep', difficulty: 'Beginner', duration: '~50 min', description: 'Map & compass reading, emergency go-bag preparation, and off-grid logistics.', tags: ['Navigation', 'Preparedness', 'Urban'] },
  { id: 'surv-4', category: 'survival', categoryLabel: 'Survival Skills', title: 'Off-Grid Solar & Battery Setup', difficulty: 'Advanced', duration: '~2h 00m', description: 'Calculate power loads, wire solar panels, and maintain backup battery banks.', tags: ['Solar', 'Electricity', 'Off-Grid'] },
  { id: 'creative-1', category: 'creative', categoryLabel: 'Creative Skills', title: 'UI/UX Design & Design Tokens', difficulty: 'Beginner', duration: '~1h 30m', description: 'Master Figma auto-layout, typographic scales, design tokens, and user testing.', tags: ['Figma', 'UI/UX', 'Design'] },
  { id: 'creative-2', category: 'creative', categoryLabel: 'Creative Skills', title: 'Motion Graphics & Logo Animation', difficulty: 'Intermediate', duration: '~1h 45m', description: 'Keyframe choreography, bezier easing, UI micro-interactions, and vector animation.', tags: ['AfterEffects', 'Animation', 'Motion'] },
  { id: 'bus-1', category: 'business', categoryLabel: 'Business Skills', title: 'Lean Startup Product Validation', difficulty: 'Beginner', duration: '~1h 15m', description: 'Test problem-solution fit, conduct customer discovery interviews, and model CAC/LTV.', tags: ['LeanStartup', 'Product', 'Business'] },
  { id: 'lang-1', category: 'languages', categoryLabel: 'Languages Skills', title: 'Conversational Spanish & Fluency', difficulty: 'Beginner', duration: '~1h 00m', description: 'High-frequency conversational dialogue, practical pronunciation, and travel fluency.', tags: ['Spanish', 'Language', 'Tandem'] }
];

/* ---------- API HELPERS ---------- */
async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'API error');
  }
  return res.json();
}

async function refreshCurrentUser() {
  if (!currentUser) return;
  const data = await api(`/api/users/${currentUser.id}`);
  currentUser = { ...currentUser, ...data };
}

async function refreshCommunitySkills() {
  const data = await api('/api/community/skills');
  communitySkills = data.listings || [];
}

async function refreshSessions() {
  if (!currentUser) return;
  sessions = await api(`/api/sessions?user_id=${currentUser.id}`);
}

async function refreshAllUsers() {
  allUsers = await api('/api/users');
}

async function refreshGroupRooms() {
  if (!currentUser) return;
  try {
    const data = await api(`/api/groups?user_id=${currentUser.id}`);
    groupRooms = data.rooms || [];
  } catch (e) {
    groupRooms = [];
  }
}

async function refreshPrivateConversations() {
  if (!currentUser) return;
  try {
    const data = await api(`/api/messages/private/conversations/${currentUser.id}`);
    privateConversations = data.conversations || [];
  } catch (e) {
    privateConversations = [];
  }
}

async function saveLinkedInUrl() {
  const urlInput = document.getElementById('linkedin_input');
  if (!urlInput) return;
  const linkedin_url = urlInput.value.trim();
  try {
    const data = await api(`/api/users/${currentUser.id}/profile`, {
      method: 'PUT',
      body: JSON.stringify({ linkedin_url })
    });
    currentUser.linkedin_url = data.linkedin_url;
    toast('LinkedIn profile proof saved successfully!');
    render();
  } catch (e) {
    toast('Failed to save LinkedIn: ' + e.message);
  }
}

function openCourseModal(domainKey) {
  const course = DOMAIN_COURSES[domainKey] || DOMAIN_COURSES['tech'];
  activeCourseModal = course;
  activeQuizAnswers = {};
  render();
}

function closeCourseModal() {
  activeCourseModal = null;
  activeQuizAnswers = {};
  render();
}

function selectQuizOption(qIndex, optIndex) {
  activeQuizAnswers[qIndex] = optIndex;
  render();
}

async function submitCourseQuiz() {
  if (!activeCourseModal) return;
  const quiz = activeCourseModal.quiz || [];
  for (let i = 0; i < quiz.length; i++) {
    if (activeQuizAnswers[i] === undefined) {
      toast(`Please answer question ${i + 1} to complete your certification.`);
      return;
    }
  }

  let correctCount = 0;
  for (let i = 0; i < quiz.length; i++) {
    if (activeQuizAnswers[i] === quiz[i].correct) {
      correctCount++;
    }
  }

  if (correctCount < quiz.length) {
    toast(`Score: ${correctCount}/${quiz.length}. Review questions and try again to achieve 100%!`);
    return;
  }

  try {
    const res = await api('/api/courses/complete', {
      method: 'POST',
      body: JSON.stringify({
        user_id: currentUser.id,
        domain: activeCourseModal.domain,
        course_title: activeCourseModal.title,
        score: 100
      })
    });
    await refreshCurrentUser();
    const completedDomain = activeCourseModal.domain;
    activeCourseModal = null;
    toast(`🎉 ${res.message}`);
    render();
  } catch (e) {
    toast('Course completion failed: ' + e.message);
  }
}

/* ---------- UTILITY FUNCTIONS ---------- */
function toast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2600);
}

function getInitials(name) {
  if (!name) return 'M';
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
}

function getDomainLabel(domain) {
  const map = {
    tech: '💻 Tech', soft: '🗣️ Soft Skill', survival: '🏕️ Survival',
    creative: '🎨 Creative', languages: '🗣️ Languages', business: '💼 Business'
  };
  return map[domain] || (domain || 'tech').toUpperCase();
}

function isFreeSkill(feeStr) {
  if (!feeStr) return false;
  const f = feeStr.toLowerCase();
  return f.includes('free') || f.includes('0 credit') || f.includes('0 mg') || f.includes('no cost');
}

/* ---------- ROUTING ---------- */
function go(v) { view = v; render(); }

function onSidebarPriceChange(val) { sidebarPriceFilter = val; render(); }
function onSidebarLevelChange(val) { sidebarLevelFilter = val; render(); }
function resetSidebarFilters() {
  sidebarPriceFilter = 'all'; sidebarLevelFilter = 'all'; homeFilterTab = 'all';
  toast('Sidebar filters reset.'); render();
}
function applyMoreSidebarFilters() { if (view !== 'home') go('home'); toast('Marketplace filters applied!'); }

/* ---------- HEADER & SIDEBAR ---------- */
function renderHeader() {
  const hr = document.getElementById('headerRight');
  if (!hr) return;
  if (!currentUser) { hr.innerHTML = ''; return; }
  hr.innerHTML = `
    <div style="display:flex;align-items:center;gap:12px;">
      <span class="mg-coin-pill">🪙 <span>${currentUser.balance}</span> MG Coins</span>
    </div>
  `;
}

function renderSidebar() {
  const sb = document.getElementById('sidebar');
  if (!sb) return;
  if (!currentUser) { sb.style.display = 'none'; return; }
  sb.style.display = 'flex';
  const pendingRequests = sessions.filter(s => s.teacher_id === currentUser.id && s.status === 'REQUESTED').length;

  sb.innerHTML = `
    <div>
      <div class="sidebar-header">
        <div class="title">Category</div>
        <div class="back-btn" onclick="resetSidebarFilters()" title="Reset Filters">←</div>
      </div>
      <div class="sidebar-filter-group">
        <div class="sidebar-filter-label"><span>Price</span><span class="sidebar-filter-reset" onclick="resetSidebarFilters()">Reset</span></div>
        <select class="sidebar-select" onchange="onSidebarPriceChange(this.value)">
          <option value="all" ${sidebarPriceFilter==='all'?'selected':''}>All Price Models</option>
          <option value="free" ${sidebarPriceFilter==='free'?'selected':''}>Free Peer Exchange</option>
          <option value="1credit" ${sidebarPriceFilter==='1credit'?'selected':''}>🪙 1 MG / Session</option>
        </select>
      </div>
      <div class="sidebar-filter-group">
        <div class="sidebar-filter-label"><span>Domain</span><span class="sidebar-more-badge" onclick="setHomeFilterTab('all')">+ 90 more</span></div>
        <div class="sidebar-quick-pills">
          <div class="sidebar-quick-pill ${homeFilterTab==='tech'?'active':''}" onclick="setHomeFilterTab('tech')" title="Tech">💻</div>
          <div class="sidebar-quick-pill ${homeFilterTab==='soft'?'active':''}" onclick="setHomeFilterTab('soft')" title="Soft Skills">🗣️</div>
          <div class="sidebar-quick-pill ${homeFilterTab==='survival'?'active':''}" onclick="setHomeFilterTab('survival')" title="Survival">🏕️</div>
          <div class="sidebar-quick-pill ${homeFilterTab==='creative'?'active':''}" onclick="setHomeFilterTab('creative')" title="Creative">🎨</div>
        </div>
      </div>
      <div class="sidebar-filter-group">
        <div class="sidebar-filter-label"><span>Condition</span></div>
        <select class="sidebar-select" onchange="onSidebarLevelChange(this.value)">
          <option value="all" ${sidebarLevelFilter==='all'?'selected':''}>Show all skills</option>
          <option value="beginner" ${sidebarLevelFilter==='beginner'?'selected':''}>Beginner level</option>
          <option value="intermediate" ${sidebarLevelFilter==='intermediate'?'selected':''}>Intermediate level</option>
          <option value="advanced" ${sidebarLevelFilter==='advanced'?'selected':''}>Advanced level</option>
        </select>
      </div>
      <div class="sidebar-menu" style="margin-top:10px;">
        <div class="sidebar-item ${view==='home'?'active':''}" onclick="go('home')"><span class="icon">🏠</span> <span>Marketplace (Home)</span></div>
        <div class="sidebar-item add-btn ${view==='add_skill'?'active':''}" onclick="openAddSkillPage()"><span class="icon">➕</span> <span>Add Detailed Skill</span></div>
        <div class="sidebar-title">Navigation</div>
        <div class="sidebar-item ${view==='dashboard'?'active':''}" onclick="go('dashboard')"><span class="icon">🎁</span> <span>Free Skills Tracks</span></div>
        <div class="sidebar-item ${view==='profile'?'active':''}" onclick="go('profile')"><span class="icon">📚</span> <span>My Skills</span></div>
        <div class="sidebar-item ${view==='community'||view==='groups'||view==='group_chat'?'active':''}" onclick="openCommunityView()"><span class="icon">🌐</span> <span>Community Hub ${groupRooms.length > 0 ? `<span style="background:var(--primary);color:#fff;font-size:0.7rem;padding:2px 6px;border-radius:10px;margin-left:auto;">${groupRooms.length}</span>` : ''}</span></div>
        <div class="sidebar-item ${view==='ai_tutor'?'active':''}" onclick="go('ai_tutor')"><span class="icon">🤖</span> <span>SkillBot AI Tutor</span></div>
        <div class="sidebar-item ${view==='requests'?'active':''}" onclick="go('requests')"><span class="icon">📩</span> <span>Requests ${pendingRequests > 0 ? `<span style="background:var(--accent-coral);color:#fff;font-size:0.7rem;padding:2px 6px;border-radius:10px;margin-left:auto;">${pendingRequests}</span>` : ''}</span></div>
        <div class="sidebar-title">Preferences</div>
        <div class="sidebar-item ${view==='account'?'active':''}" onclick="go('account')"><span class="icon">👤</span> <span>Account</span></div>
        <div class="sidebar-item ${view==='settings'?'active':''}" onclick="go('settings')"><span class="icon">⚙️</span> <span>Settings</span></div>
      </div>
      <button class="dark-filter-btn" onclick="applyMoreSidebarFilters()">More Filters</button>
    </div>
    <div style="margin-top:14px;">
      <div class="sidebar-divider"></div>
      <div class="sidebar-item" onclick="logout()" style="color:var(--accent-coral);"><span class="icon">🚪</span> <span>Log Out</span></div>
      <div class="sidebar-user-preview" style="margin-top:6px;">
        <div class="user-avatar" style="width:32px;height:32px;font-size:0.8rem;">${getInitials(currentUser.name)}</div>
        <div style="overflow:hidden;">
          <div class="name">${currentUser.name}</div>
          <div class="email">${currentUser.email}</div>
        </div>
      </div>
      <div style="font-size:0.72rem;color:var(--text-dim);text-align:center;margin-top:10px;line-height:1.4;">
        Built with ❤️ for Buildathon<br>by <strong>Dharshin R</strong> & <strong>Mohammed Sanjidh S</strong>
      </div>
    </div>
  `;
}

function logout() { currentUser = null; sessions = []; communitySkills = []; go('login'); }

/* ---------- LOGIN ---------- */
function renderLogin() {
  return `
  <div class="card" style="max-width:440px;margin:50px auto;text-align:center;">
    <img src="logo.jpg" alt="MOGG Logo" style="width:72px;height:72px;border-radius:18px;margin:0 auto 16px;object-fit:cover;box-shadow:var(--shadow-md);border:1px solid var(--border-color);display:block;">
    <h1>Welcome to MOGG</h1>
    <p class="sub">Trade what you know for what you want to learn.</p>
    <div style="text-align:left;">
      <label>Full Name</label>
      <input id="li_name" placeholder="e.g. Aanya Menon">
      <label>Email Address</label>
      <input id="li_email" placeholder="you@example.com">
      <button class="btn" style="margin-top:20px;width:100%" onclick="doLogin()">Get Started</button>
    </div>
    <div style="margin-top:24px;padding-top:18px;border-top:1px solid var(--border-color);">
      <p style="font-size:0.82rem;color:var(--text-dim);margin-bottom:10px;">Quick demo login as sample peer:</p>
      <div class="demo-users-row" style="justify-content:center;">
        <button class="demo-user-btn" onclick="quickLogin('Alex Rivera','alex@mogg.io')">Alex (UI Designer)</button>
        <button class="demo-user-btn" onclick="quickLogin('Sofia Chen','sofia@mogg.io')">Sofia (Python AI)</button>
        <button class="demo-user-btn" onclick="quickLogin('Marcus Vance','marcus@mogg.io')">Marcus (Musician)</button>
        <button class="demo-user-btn" onclick="quickLogin('David Kim','david@mogg.io')">David (Cloud Security)</button>
      </div>
      <div style="margin-top:16px;font-size:0.75rem;color:var(--text-dim);line-height:1.4;">
        Engineered with ❤️ for Buildathon<br>by <strong>Dharshin R</strong> & <strong>Mohammed Sanjidh S</strong>
      </div>
    </div>
  </div>`;
}

async function doLogin() {
  const name = document.getElementById('li_name')?.value.trim();
  const email = document.getElementById('li_email')?.value.trim().toLowerCase();
  if (!name || !email) { toast('Please enter both your name and email to continue.'); return; }
  try {
    const data = await api('/api/auth/login', { method: 'POST', body: JSON.stringify({ name, email }) });
    currentUser = data;
    toast(data.is_new ? 'Account created! You received free MG Coins.' : 'Welcome back, ' + data.name + '!');
    await Promise.all([refreshCommunitySkills(), refreshSessions(), refreshAllUsers(), refreshGroupRooms(), refreshPrivateConversations()]);
    go('home');
  } catch (e) { toast('Login failed: ' + e.message); }
}

async function quickLogin(name, email) {
  try {
    const data = await api('/api/auth/login', { method: 'POST', body: JSON.stringify({ name, email }) });
    currentUser = data;
    toast('Logged in as ' + data.name);
    await Promise.all([refreshCommunitySkills(), refreshSessions(), refreshAllUsers(), refreshGroupRooms(), refreshPrivateConversations()]);
    go('home');
  } catch (e) { toast('Login failed: ' + e.message); }
}

/* ---------- HOME / MARKETPLACE ---------- */
function setHomeFilterTab(tab) { homeFilterTab = tab; render(); }

function renderHomePage() {
  const listings = communitySkills;
  const counts = {
    all: listings.length,
    free: listings.filter(i => isFreeSkill(i.fee_text)).length,
    tech: listings.filter(i => i.domain === 'tech').length,
    soft: listings.filter(i => i.domain === 'soft').length,
    survival: listings.filter(i => i.domain === 'survival').length,
    creative: listings.filter(i => i.domain === 'creative').length,
    languages: listings.filter(i => i.domain === 'languages').length,
    business: listings.filter(i => i.domain === 'business').length
  };

  const filtered = listings.filter(item => {
    if (homeFilterTab === 'free' && !isFreeSkill(item.fee_text)) return false;
    if (homeFilterTab !== 'all' && homeFilterTab !== 'free' && item.domain !== homeFilterTab) return false;
    if (sidebarPriceFilter === 'free' && !isFreeSkill(item.fee_text)) return false;
    if (sidebarPriceFilter === '1credit' && !(item.fee_text || '').includes('1 Credit')) return false;
    if (sidebarLevelFilter !== 'all') {
      const d = (item.description || '').toLowerCase();
      const n = (item.skill_text || '').toLowerCase();
      if (!d.includes(sidebarLevelFilter) && !n.includes(sidebarLevelFilter)) return false;
    }
    return true;
  });

  return `
  <div class="market-hero-banner">
    <div class="hero-title">MOGG SKILL EXCHANGE</div>
    <div class="hero-subtitle">Explore live skills offered by community tutors. Learn real-world tech, soft skills, survival, design, languages, and business strategies directly from peers.</div>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:18px;">
    <div><h2>Skills Offered by Community Tutors (${filtered.length})</h2><p class="sub" style="margin-bottom:0">Browse verified skill listings offered by community members for exchange.</p></div>
    <button class="btn sm" onclick="openAddSkillPage()">+ Offer My Skill</button>
  </div>
  <div class="filter-tabs">
    <button class="filter-tab ${homeFilterTab==='all'?'active':''}" onclick="setHomeFilterTab('all')">All Listings (${counts.all})</button>
    <button class="filter-tab ${homeFilterTab==='free'?'active':''}" onclick="setHomeFilterTab('free')">🎁 Free Skills Only (${counts.free})</button>
    <button class="filter-tab ${homeFilterTab==='tech'?'active':''}" onclick="setHomeFilterTab('tech')">💻 Tech (${counts.tech})</button>
    <button class="filter-tab ${homeFilterTab==='soft'?'active':''}" onclick="setHomeFilterTab('soft')">🗣️ Soft Skills (${counts.soft})</button>
    <button class="filter-tab ${homeFilterTab==='survival'?'active':''}" onclick="setHomeFilterTab('survival')">🏕️ Survival (${counts.survival})</button>
    <button class="filter-tab ${homeFilterTab==='creative'?'active':''}" onclick="setHomeFilterTab('creative')">🎨 Creative (${counts.creative})</button>
    <button class="filter-tab ${homeFilterTab==='languages'?'active':''}" onclick="setHomeFilterTab('languages')">🗣️ Languages (${counts.languages})</button>
    <button class="filter-tab ${homeFilterTab==='business'?'active':''}" onclick="setHomeFilterTab('business')">💼 Business (${counts.business})</button>
  </div>
  ${filtered.length === 0 ?
    '<div class="card"><div class="empty">No skill listings found in this category. Click "+ Offer My Skill" to publish the first one!</div></div>' :
    `<div class="market-grid">${filtered.map(item => renderMarketCard(item)).join('')}</div>`}
  `;
}

function renderMarketCard(item) {
  const isFree = isFreeSkill(item.fee_text);
  const domainLabel = getDomainLabel(item.domain);
  const isMe = currentUser && item.seller_id === currentUser.id;

  return `
    <div class="market-card">
      <div onclick="openSkillDetail(${item.id}, ${item.seller_id})" style="cursor:pointer;">
        <div class="market-card-placeholder">🎯</div>
        <div class="market-card-body">
          <div class="seller-info">
            <div class="seller-avatar">${getInitials(item.seller_name)}</div>
            <div style="overflow:hidden;flex:1;">
              <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
                <div class="seller-name">${item.seller_name} ${isMe ? '<small style="color:var(--primary)">(You)</small>' : ''}</div>
                ${item.seller_linkedin ? `<a href="${item.seller_linkedin}" target="_blank" class="linkedin-badge" onclick="event.stopPropagation()" title="Verified LinkedIn Profile">💼 in</a>` : ''}
              </div>
              <div class="seller-bio-snippet">${item.seller_bio || item.seller_email}</div>
            </div>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span class="domain-tag ${item.domain}">${domainLabel}</span>
            <span class="${isFree ? 'free-badge' : 'fee-pill mg'}">${item.fee_text || '🪙 1 MG'}</span>
          </div>
          <div class="skill-card-title">${item.skill_text}</div>
          <div class="skill-card-desc">${item.description || 'Interactive practical trading session.'}</div>
        </div>
      </div>
      <div style="padding:0 18px 18px 18px;display:flex;gap:8px;">
        ${isMe ?
          `<button class="btn secondary sm" style="width:100%" onclick="openAddSkillPage(${item.id}, 'teach')">Edit My Listing</button>` :
          `<button class="btn secondary sm" style="flex:1" onclick="openSkillDetail(${item.id}, ${item.seller_id})">View Details</button>
           <button class="btn sm" style="flex:1" onclick="purchaseSkill(${item.id}, ${item.seller_id}, '${item.skill_text.replace(/'/g, "\\'")}')">Purchase Skill</button>`}
      </div>
    </div>
  `;
}

/* ---------- SKILL PURCHASE (API-backed) ---------- */
async function purchaseSkill(listingId, sellerId, skillText) {
  if (!currentUser) return;
  if (sellerId === currentUser.id) { toast("You can't purchase your own skill!"); return; }
  try {
    const result = await api('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({
        session_type: 'CREDIT_EXCHANGE',
        teacher_id: sellerId,
        learner_id: currentUser.id,
        teach_skill_text: skillText
      })
    });
    await Promise.all([refreshCurrentUser(), refreshSessions()]);
    toast(`Session requested for "${skillText}"! Check Requests page.`);
    go('requests');
  } catch (e) { toast('Purchase failed: ' + e.message); }
}

/* ---------- SKILL DETAIL PAGE ---------- */
function openSkillDetail(listingId, sellerId) {
  activeSkillDetailState = { listingId, sellerId };
  activePaymentMethod = 'mg';
  isPaymentModalOpen = false;
  go('skill_detail');
}

function setPaymentMethod(method) { activePaymentMethod = method; render(); }
function openCheckoutModal() { isPaymentModalOpen = true; render(); }
function closeCheckoutModal() { isPaymentModalOpen = false; render(); }

function renderSkillDetailPage() {
  if (!activeSkillDetailState) return renderHomePage();
  const { listingId, sellerId } = activeSkillDetailState;
  const skill = communitySkills.find(s => s.id === listingId);
  const sellerData = allUsers.find(u => u.id === sellerId);
  if (!skill || !sellerData) return renderHomePage();

  const domainLabel = getDomainLabel(skill.domain);
  const myTeach = currentUser?.teach_listings || [];
  const isMe = currentUser && sellerId === currentUser.id;

  return `
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
    <div>
      <span class="domain-tag ${skill.domain}" style="margin-bottom:6px;display:inline-block;">${domainLabel}</span>
      <h1>${skill.skill_text}</h1>
      <p class="sub" style="margin-bottom:0">Offered by verified community tutor <strong>${sellerData.name}</strong></p>
    </div>
    <button class="btn ghost sm" onclick="go('home')">← Back to Marketplace</button>
  </div>

  <div class="skill-detail-hero">
    <div class="skill-detail-hero-placeholder">🎯</div>
  </div>

  <div class="skill-detail-grid">
    <div>
      <div class="tutor-detail-card">
        <div class="tutor-avatar-lg">${getInitials(sellerData.name)}</div>
        <div style="flex:1;">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
            <div style="font-weight:700;font-size:1.1rem;color:var(--text-primary)">${sellerData.name} ${isMe ? '(You)' : ''}</div>
            ${sellerData.linkedin_url ? `
              <a href="${sellerData.linkedin_url}" target="_blank" class="linkedin-btn" style="padding:5px 12px;font-size:0.8rem;">
                <span>💼 Verified LinkedIn Profile</span> ↗
              </a>
            ` : ''}
          </div>
          <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:2px;">${sellerData.bio || sellerData.email}</div>
          <div style="margin-top:6px;display:flex;gap:8px;flex-wrap:wrap;">
            <span style="font-size:0.75rem;background:#d1fae5;color:#047857;padding:2px 8px;border-radius:10px;font-weight:700;">Verified Tutor</span>
            <span style="font-size:0.75rem;background:#e0f2fe;color:#0369a1;padding:2px 8px;border-radius:10px;font-weight:700;">98% Positive Feedback</span>
            ${(sellerData.certifications || []).map(c => `<span class="domain-cert-badge" style="font-size:0.75rem;">🎓 ${getDomainLabel(c)} Certified</span>`).join('')}
          </div>
        </div>
      </div>
      <div class="card">
        <h2>Detailed Course Breakdown & Curriculum</h2>
        <p style="font-size:0.95rem;color:var(--text-secondary);line-height:1.6;margin-bottom:16px;">${skill.description || 'Comprehensive 1-on-1 practical trade session covering fundamental principles.'}</p>
        <h3 style="font-size:1rem;margin:16px 0 10px;color:var(--text-primary)">What you will master:</h3>
        <ul style="padding-left:20px;color:var(--text-secondary);font-size:0.9rem;line-height:1.7;">
          <li>Core architectural concepts & tool setups</li>
          <li>Step-by-step practical implementation under 1-on-1 tutor guidance</li>
          <li>Direct Q&A, code review, and personalized skill feedback</li>
          <li>Verified completion certificate added to your MOGG profile</li>
        </ul>
      </div>
    </div>
    <div class="card" style="position:sticky;top:85px;">
      <h2 style="margin-bottom:4px;">Acquire & Purchase Skill</h2>
      <p style="font-size:0.83rem;color:var(--text-dim);margin-bottom:16px;">Select your preferred payment or skill trade option to instantly unlock this course.</p>
      <div style="display:flex;align-items:center;justify-content:space-between;padding:12px;background:#f8fafc;border-radius:12px;margin-bottom:16px;">
        <span style="font-size:0.88rem;color:var(--text-secondary);font-weight:600;">Skill Listing Fee:</span>
        <span class="fee-pill mg" style="font-size:0.9rem;">${skill.fee_text || '🪙 1 MG'}</span>
      </div>
      <label>Choose Acquisition Method</label>
      <div class="payment-options-grid">
        <div class="payment-option-card ${activePaymentMethod==='mg'?'active':''}" onclick="setPaymentMethod('mg')">
          <div class="payment-option-left"><div class="payment-icon">🪙</div><div><div class="payment-option-title">Pay with MG Coins</div><div class="payment-option-sub">Balance: 🪙 ${currentUser?.balance || 0} MG available</div></div></div>
          <input type="radio" name="pay_method" ${activePaymentMethod==='mg'?'checked':''}>
        </div>
        <div class="payment-option-card ${activePaymentMethod==='trade'?'active':''}" onclick="setPaymentMethod('trade')">
          <div class="payment-option-left"><div class="payment-icon">🔄</div><div><div class="payment-option-title">Trade with My Skill</div><div class="payment-option-sub">Exchange 1-on-1 with a skill you offer</div></div></div>
          <input type="radio" name="pay_method" ${activePaymentMethod==='trade'?'checked':''}>
        </div>
      </div>
      ${activePaymentMethod === 'trade' && myTeach.length ? `
        <div style="margin-bottom:16px;">
          <label>Select Your Skill to Exchange</label>
          <select id="trade_skill_select" class="sidebar-select">
            ${myTeach.map(s => `<option value="${s.skill_text}">${s.skill_text} (${s.domain})</option>`).join('')}
          </select>
        </div>
      ` : ''}
      ${isMe ?
        `<button class="btn secondary" style="width:100%" disabled>This is your own skill listing</button>` :
        activePaymentMethod === 'trade' ?
        `<button class="btn" style="width:100%" onclick="purchaseSkillTrade(${listingId}, ${sellerId}, '${skill.skill_text.replace(/'/g, "\\'")}')">Confirm Skill Trade</button>` :
        `<button class="btn" style="width:100%" onclick="purchaseSkill(${listingId}, ${sellerId}, '${skill.skill_text.replace(/'/g, "\\'")}')">Purchase with 🪙 1 MG</button>`}
    </div>
  </div>
  `;
}

async function purchaseSkillTrade(listingId, sellerId, skillText) {
  const tradeSkill = document.getElementById('trade_skill_select')?.value || 'Skill Exchange';
  try {
    await api('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({
        session_type: 'DIRECT_TRADE',
        teacher_id: sellerId,
        learner_id: currentUser.id,
        teach_skill_text: skillText,
        trade_skill_text: tradeSkill
      })
    });
    await Promise.all([refreshCurrentUser(), refreshSessions()]);
    toast(`Trade request sent for "${skillText}"!`);
    go('requests');
  } catch (e) { toast('Trade failed: ' + e.message); }
}

/* ---------- MY SKILLS (PROFILE) ---------- */
function setMySkillsTab(tab) { mySkillsActiveTab = tab; render(); }

function renderProfile() {
  const teach = currentUser?.teach_listings || [];
  const purchased = sessions.filter(s => (s.status === 'ACCEPTED' || s.status === 'CREDIT_RELEASED'));
  const ongoing = sessions.filter(s => s.status === 'ACCEPTED');
  const completed = sessions.filter(s => s.status === 'CREDIT_RELEASED');

  return `
  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:18px;">
    <div><h1>My Skills Dashboard</h1><p class="sub" style="margin-bottom:0">Track your purchased skills, ongoing sessions, completed milestones, and offered trade skills.</p></div>
    <button class="btn sm" onclick="openAddSkillPage()">+ Offer New Skill</button>
  </div>
  <div class="my-skills-tabs">
    <div class="my-skills-tab ${mySkillsActiveTab==='purchased'?'active':''}" onclick="setMySkillsTab('purchased')"><span>🛒 Purchased Skills (${purchased.length})</span></div>
    <div class="my-skills-tab ${mySkillsActiveTab==='ongoing'?'active':''}" onclick="setMySkillsTab('ongoing')"><span>⏳ Ongoing Skills (${ongoing.length})</span></div>
    <div class="my-skills-tab ${mySkillsActiveTab==='completed'?'active':''}" onclick="setMySkillsTab('completed')"><span>✅ Completed Skills (${completed.length})</span></div>
    <div class="my-skills-tab ${mySkillsActiveTab==='offered'?'active':''}" onclick="setMySkillsTab('offered')"><span>📚 Offered Skills (${teach.length})</span></div>
  </div>
  ${renderMySkillsTabContent(purchased, ongoing, completed, teach)}
  <div class="card" style="margin-top:24px;">
    <h2>Short Bio & Member Summary</h2>
    <textarea id="bioInput" placeholder="Write a short summary about yourself...">${currentUser?.bio || ''}</textarea>
    <button class="btn" style="margin-top:12px" onclick="saveBio()">Save Bio</button>
  </div>
  <div class="card" style="margin-top:24px;">
    <h2>💼 Professional Proof & LinkedIn Verification</h2>
    <p class="sub" style="margin-bottom:12px;">Link your verified LinkedIn profile URL to show peer learners and trading partners proof of your real-world experience.</p>
    <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
      <input id="linkedin_input" placeholder="https://www.linkedin.com/in/your-username" value="${currentUser?.linkedin_url || ''}" style="flex:1;min-width:260px;margin:0;">
      <button class="btn" style="background:#0077b5;" onclick="saveLinkedInUrl()">Save LinkedIn Proof</button>
      ${currentUser?.linkedin_url ? `<a href="${currentUser.linkedin_url}" target="_blank" class="linkedin-badge" style="font-size:0.85rem;padding:9px 14px;">View Profile ↗</a>` : ''}
    </div>
    <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
      <span style="font-size:0.82rem;font-weight:700;color:var(--text-secondary);">Your Verified Teaching Certifications:</span>
      ${(currentUser?.certifications || []).length ? (currentUser.certifications).map(c => `
        <span class="domain-cert-badge" style="font-size:0.8rem;padding:4px 10px;">🎓 ${getDomainLabel(c)} Certified</span>
      `).join('') : '<span style="font-size:0.82rem;color:var(--text-dim);">No domain certifications yet. Visit Free Skills Tracks to take crash courses & earn certifications!</span>'}
    </div>
  </div>
  `;
}

function renderMySkillsTabContent(purchased, ongoing, completed, teach) {
  if (mySkillsActiveTab === 'purchased') {
    return `<div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;"><h2>🛒 Purchased & Unlocked Skills (${purchased.length})</h2></div>
      ${purchased.length === 0 ? '<div class="empty">No purchased skills yet. Explore the Marketplace!</div>' :
        `<div class="skills-detail-grid">${purchased.map(r => {
          const isSeller = r.teacher_id === currentUser.id;
          const peerName = isSeller ? r.learner_name : r.teacher_name;
          return `<div class="detailed-skill-card">
            <div class="skill-card-placeholder" style="background:linear-gradient(135deg,#fffbeb 0%,#fde68a 100%);color:#b45309">🪙</div>
            <div class="skill-card-body">
              <div class="skill-card-header"><span class="status-badge purchased">Purchased</span></div>
              <div class="skill-card-title">${r.teach_skill}</div>
              <div class="skill-card-desc">Trade Partner: <strong>${peerName}</strong> (${isSeller ? 'Learner' : 'Tutor'})</div>
              <div class="skill-card-actions"><button class="btn sm" onclick="openChat(${r.id})">Open Session Chat</button></div>
            </div>
          </div>`;
        }).join('')}</div>`}
    </div>`;
  }
  if (mySkillsActiveTab === 'ongoing') {
    return `<div class="card">
      <h2>⏳ Ongoing Active Skills (${ongoing.length})</h2>
      ${ongoing.length === 0 ? '<div class="empty">No ongoing sessions at the moment.</div>' :
        `<div class="skills-detail-grid">${ongoing.map(r => {
          const peerName = r.teacher_id === currentUser.id ? r.learner_name : r.teacher_name;
          return `<div class="detailed-skill-card">
            <div class="skill-card-placeholder" style="background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%);color:#b45309">⏳</div>
            <div class="skill-card-body">
              <div class="skill-card-header"><span class="status-badge ongoing">In-Progress</span></div>
              <div class="skill-card-title">${r.teach_skill}</div>
              <div class="skill-card-desc">Partner: <strong>${peerName}</strong></div>
              <div class="skill-card-actions">
                <button class="btn sm" onclick="openChat(${r.id})">Open Chat</button>
                <button class="btn secondary sm" onclick="completeSession(${r.id})">Mark Completed</button>
              </div>
            </div>
          </div>`;
        }).join('')}</div>`}
    </div>`;
  }
  if (mySkillsActiveTab === 'completed') {
    return `<div class="card">
      <h2>✅ Completed Skill Milestones (${completed.length})</h2>
      ${completed.length === 0 ? '<div class="empty">No completed skills yet.</div>' :
        `<div class="skills-detail-grid">${completed.map(r => {
          const peerName = r.teacher_id === currentUser.id ? r.learner_name : r.teacher_name;
          return `<div class="detailed-skill-card">
            <div class="skill-card-placeholder" style="background:linear-gradient(135deg,#d1fae5 0%,#a7f3d0 100%);color:#047857">🏆</div>
            <div class="skill-card-body">
              <div class="skill-card-header"><span class="status-badge completed">✅ Completed</span></div>
              <div class="skill-card-title">${r.teach_skill}</div>
              <div class="skill-card-desc">Taught by <strong>${peerName}</strong></div>
              <div class="skill-card-actions"><span style="font-size:0.78rem;color:var(--accent-emerald);font-weight:600;">Verified Skill Badge</span></div>
            </div>
          </div>`;
        }).join('')}</div>`}
    </div>`;
  }
  // Offered
  return `<div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
      <h2>📚 Skills Offered to Teach (${teach.length})</h2>
      <button class="btn secondary sm" onclick="openAddSkillPage(null, 'teach')">+ Add Teaching Skill</button>
    </div>
    ${teach.length === 0 ? '<div class="empty">No teaching skills added yet.</div>' :
      `<div class="skills-detail-grid">${teach.map(sk => `
        <div class="detailed-skill-card">
          <div class="skill-card-placeholder">🎯</div>
          <div class="skill-card-body">
            <div class="skill-card-header">
              <span class="domain-tag ${sk.domain}">${getDomainLabel(sk.domain)}</span>
              <span class="fee-pill">${sk.fee_text || '⚡ 1 Credit'}</span>
            </div>
            <div class="skill-card-title">${sk.skill_text}</div>
            <div class="skill-card-desc">${sk.description || ''}</div>
            <div class="skill-card-actions">
              <button class="btn ghost sm" style="color:var(--accent-coral)" onclick="deleteSkill(${sk.id})">Delete</button>
            </div>
          </div>
        </div>
      `).join('')}</div>`}
  </div>`;
}

async function saveBio() {
  const bio = document.getElementById('bioInput')?.value.trim() || '';
  try {
    await api(`/api/users/${currentUser.id}/bio`, { method: 'PUT', body: JSON.stringify({ bio }) });
    currentUser.bio = bio;
    toast('Bio saved successfully.');
  } catch (e) { toast('Failed to save bio: ' + e.message); }
}

async function deleteSkill(listingId) {
  try {
    await api(`/api/listings/${listingId}?user_id=${currentUser.id}`, { method: 'DELETE' });
    await refreshCurrentUser();
    toast('Skill removed.');
    render();
  } catch (e) { toast('Delete failed: ' + e.message); }
}

async function completeSession(sessionId) {
  try {
    await api(`/api/sessions/${sessionId}/complete`, { method: 'POST', body: JSON.stringify({ user_id: currentUser.id }) });
    await Promise.all([refreshCurrentUser(), refreshSessions()]);
    toast('Session marked as completed!');
    render();
  } catch (e) { toast('Error: ' + e.message); }
}

/* ---------- ADD SKILL ---------- */
function openAddSkillPage(skillId = null, presetType = 'teach') {
  addSkillFormState = { id: skillId, type: presetType, domain: 'tech', name: '', fee: '⚡ 1 Credit / Session', description: '', image: '' };
  go('add_skill');
}

function setAddSkillDomain(domain) { addSkillFormState.domain = domain; render(); }
function setPresetFee(fee) { addSkillFormState.fee = fee; const el = document.getElementById('as_fee'); if (el) el.value = fee; }

function renderAddSkillPage() {
  const s = addSkillFormState;
  const isTeach = s.type === 'teach';
  const isCertified = (currentUser?.certifications || []).includes(s.domain);

  return `
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;">
    <div><h1>Create Detailed Skill Listing</h1><p class="sub" style="margin-bottom:0">Fill out your skill information.</p></div>
    <button class="btn ghost sm" onclick="go('profile')">← Back to My Skills</button>
  </div>
  <div class="card">
    <h2 style="margin-bottom:18px">Skill Details Form</h2>
    <div class="row"><div>
      <label>Listing Type</label>
      <select id="as_type" onchange="addSkillFormState.type = this.value; render();">
        <option value="teach" ${s.type==='teach'?'selected':''}>Skill I Can Teach (Requires Certification)</option>
        <option value="learn" ${s.type==='learn'?'selected':''}>Skill I Want to Learn (No Restriction)</option>
      </select>
    </div></div>

    <label>Select Domain / Category</label>
    <div class="domain-tiles-grid">
      ${['tech', 'soft', 'survival', 'creative', 'languages', 'business'].map(d => {
        const isCert = (currentUser?.certifications || []).includes(d);
        return `
          <div class="domain-tile ${s.domain===d?'active':''} ${isCert?'certified':'locked'}" onclick="setAddSkillDomain('${d}')">
            <span>${getDomainLabel(d)}</span>
            <span class="${isCert ? 'domain-cert-badge' : 'domain-lock-badge'}">${isCert ? '✓' : '🔒'}</span>
          </div>
        `;
      }).join('')}
    </div>

    ${isTeach && !isCertified ? `
      <div style="background:#fffbeb;border:1px solid #fde68a;padding:14px 18px;border-radius:12px;margin:16px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
        <div>
          <div style="font-weight:700;color:#92400e;font-size:0.95rem;">🔒 Domain Training Certification Required</div>
          <div style="font-size:0.85rem;color:#b45309;margin-top:2px;">To maintain peer learning quality, you must complete the free <strong>${getDomainLabel(s.domain)}</strong> crash course & quiz before posting a teaching listing.</div>
        </div>
        <button class="btn sm" onclick="openCourseModal('${s.domain}')">🎓 Take Free Crash Course & Unlock (+2 Coins)</button>
      </div>
    ` : isTeach ? `
      <div style="background:#ecfdf5;border:1px solid #a7f3d0;padding:10px 16px;border-radius:12px;margin:14px 0;font-size:0.85rem;color:#065f46;font-weight:600;">
        ✅ You are verified & certified to teach in <strong>${getDomainLabel(s.domain)}</strong>!
      </div>
    ` : ''}

    <label>Skill Title / Name</label>
    <input id="as_name" placeholder="e.g. Fullstack React, Executive Public Speaking" value="${s.name || ''}">
    <label>Fee Details / Pricing Model</label>
    <input id="as_fee" placeholder="e.g. ⚡ 1 Credit / Session" value="${s.fee}">
    <div>
      <span class="preset-fee-btn" onclick="setPresetFee('⚡ 1 Credit / Session')">⚡ 1 Credit / Session</span>
      <span class="preset-fee-btn" onclick="setPresetFee('Free Peer Exchange')">Free Peer Exchange</span>
    </div>
    <label>Detailed Description</label>
    <textarea id="as_desc" style="min-height:110px;" placeholder="Write a detailed summary of what you will cover...">${s.description || ''}</textarea>
    <div style="display:flex;gap:12px;margin-top:28px;">
      ${isTeach && !isCertified ?
        `<button class="btn" style="flex:1;opacity:0.7;" onclick="openCourseModal('${s.domain}')">🔒 Complete ${getDomainLabel(s.domain)} Course to Publish (+2 Coins)</button>` :
        `<button class="btn" style="flex:1" onclick="submitAddSkill()">Publish Detailed Skill</button>`}
      <button class="btn secondary" onclick="go('profile')">Cancel</button>
    </div>
  </div>`;
}

async function submitAddSkill() {
  const typeEl = document.getElementById('as_type');
  const nameEl = document.getElementById('as_name');
  const feeEl = document.getElementById('as_fee');
  const descEl = document.getElementById('as_desc');
  const name = nameEl?.value.trim();
  if (!name) { toast('Please enter a skill title.'); return; }

  const isTeach = typeEl?.value !== 'learn';
  if (isTeach) {
    const isCert = (currentUser?.certifications || []).includes(addSkillFormState.domain);
    if (!isCert) {
      toast(`You must complete the free ${getDomainLabel(addSkillFormState.domain)} crash course first to unlock teaching.`);
      openCourseModal(addSkillFormState.domain);
      return;
    }
  }

  try {
    await api('/api/listings', {
      method: 'POST',
      body: JSON.stringify({
        user_id: currentUser.id,
        type: isTeach ? 'TEACH' : 'LEARN',
        skill_text: name,
        category: addSkillFormState.domain.charAt(0).toUpperCase() + addSkillFormState.domain.slice(1),
        domain: addSkillFormState.domain,
        fee_text: feeEl?.value || '⚡ 1 Credit / Session',
        description: descEl?.value || ''
      })
    });
    await Promise.all([refreshCurrentUser(), refreshCommunitySkills()]);
    toast(`Added "${name}" to your skills!`);
    go('profile');
  } catch (e) { toast('Failed: ' + e.message); }
}

/* ---------- REQUESTS ---------- */
function renderRequests() {
  const incoming = sessions.filter(s => s.teacher_id === currentUser.id);
  const outgoing = sessions.filter(s => s.learner_id === currentUser.id);

  return `
  <h1>Exchange Requests</h1>
  <p class="sub">Manage incoming proposals and active sessions.</p>
  <div class="card">
    <h2>Incoming Proposals</h2>
    ${incoming.length === 0 ? '<div class="empty">No incoming requests right now.</div>' :
      incoming.map(r => `
        <div class="match-card" style="margin-bottom:10px;">
          <div class="user-info">
            <div class="user-avatar">${getInitials(r.learner_name)}</div>
            <div>
              <div class="name">${r.learner_name}</div>
              <div class="meta">Wants to learn: <strong>${r.teach_skill}</strong></div>
              <div class="meta" style="font-size:0.8rem;">Status: <span style="text-transform:capitalize;font-weight:600;color:${r.status==='ACCEPTED'?'var(--accent-emerald)':r.status==='DECLINED'?'var(--accent-coral)':'var(--accent-amber)'}">${r.status}</span></div>
            </div>
          </div>
          <div style="display:flex;gap:8px;">
            ${r.status === 'REQUESTED' ? `
              <button class="btn sm" onclick="respondSession(${r.id}, 'accept')">Accept</button>
              <button class="btn secondary sm" onclick="respondSession(${r.id}, 'decline')">Decline</button>
            ` : r.status === 'ACCEPTED' ? `<button class="btn sm" onclick="openChat(${r.id})">Open Chat</button>` : ''}
          </div>
        </div>
      `).join('')}
  </div>
  <div class="card">
    <h2>Sent Requests</h2>
    ${outgoing.length === 0 ? `<div class="empty">You have not sent any session requests yet.</div>` :
      outgoing.map(r => `
        <div class="match-card" style="margin-bottom:10px;">
          <div class="user-info">
            <div class="user-avatar">${getInitials(r.teacher_name)}</div>
            <div>
              <div class="name">${r.teacher_name}</div>
              <div class="meta">Requested skill: <strong>${r.teach_skill}</strong></div>
              <div class="meta" style="font-size:0.8rem;">Status: <span style="text-transform:capitalize;font-weight:600;color:${r.status==='ACCEPTED'?'var(--accent-emerald)':r.status==='DECLINED'?'var(--accent-coral)':'var(--accent-amber)'}">${r.status}</span></div>
            </div>
          </div>
          <div>${r.status === 'ACCEPTED' ? `<button class="btn sm" onclick="openChat(${r.id})">Open Chat</button>` : ''}</div>
        </div>
      `).join('')}
  </div>`;
}

async function respondSession(sessionId, action) {
  try {
    await api(`/api/sessions/${sessionId}/${action}`, { method: 'POST', body: JSON.stringify({ user_id: currentUser.id }) });
    await Promise.all([refreshCurrentUser(), refreshSessions()]);
    toast(action === 'accept' ? 'Session accepted!' : 'Session declined.');
    render();
  } catch (e) { toast('Error: ' + e.message); }
}

/* ---------- CHAT ---------- */
async function openChat(sessionId) {
  activeChatSessionId = sessionId;
  try {
    chatMessages = await api(`/api/messages/${sessionId}`);
  } catch (e) { chatMessages = []; }
  go('chat');
}

function renderChat() {
  if (!activeChatSessionId) return '<div class="card"><p>No session selected.</p></div>';
  const session = sessions.find(s => s.id === activeChatSessionId);
  if (!session) return '<div class="card"><p>Session not found.</p></div>';
  const otherName = session.teacher_id === currentUser.id ? session.learner_name : session.teacher_name;

  return `
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;">
    <div><h1>Chat with ${otherName}</h1><p class="sub" style="margin-bottom:0">Trading skill: <strong>${session.teach_skill}</strong></p></div>
    <div style="display:flex;gap:8px;">
      <button class="btn secondary sm" onclick="openGroupRoomsView()">👥 Multi-Peer Study Groups</button>
      <button class="btn ghost sm" onclick="go('requests')">← Back to Requests</button>
    </div>
  </div>
  <div class="card">
    <div class="msgbox" id="msgbox">
      ${chatMessages.length ? chatMessages.map(m => {
        const isMe = m.sender_id === currentUser.id;
        return `<div class="msg ${isMe ? 'sent' : 'received'}">
          <div class="msg-author">${isMe ? 'You' : m.sender_name}</div>
          <div>${m.text}</div>
        </div>`;
      }).join('') : '<div class="empty">Send a greeting message to coordinate your exchange session!</div>'}
    </div>
    <div class="row">
      <input id="chatInput" placeholder="Type your message here..." onkeydown="if(event.key==='Enter') sendMsg()">
      <button class="btn" style="flex:0 0 auto" onclick="sendMsg()">Send</button>
    </div>
  </div>`;
}

async function sendMsg() {
  const input = document.getElementById('chatInput');
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  try {
    await api(`/api/messages/${activeChatSessionId}`, {
      method: 'POST',
      body: JSON.stringify({ sender_id: currentUser.id, text })
    });
    chatMessages = await api(`/api/messages/${activeChatSessionId}`);
    render();
    setTimeout(() => { const box = document.getElementById('msgbox'); if (box) box.scrollTop = box.scrollHeight; }, 50);
  } catch (e) { toast('Message failed: ' + e.message); }
}

/* ---------- COMMUNITY HUB (PUBLIC CHANNELS & PRIVATE PEER CHAT) ---------- */

async function openCommunityView(tab = 'channels') {
  activeCommunityTab = tab;
  await Promise.all([refreshGroupRooms(), refreshPrivateConversations()]);
  go('community');
}

function setCommunityTab(tab) {
  activeCommunityTab = tab;
  render();
}

function renderCommunityPage() {
  const rooms = groupRooms || [];
  const convos = privateConversations || [];

  return `
  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:16px;">
    <div>
      <h1 style="display:flex;align-items:center;gap:10px;">🌐 Community Hub</h1>
      <p class="sub" style="margin-bottom:0">Connect with fellow skill-swappers! Discuss openly across community channels or message trade partners privately 1-on-1.</p>
    </div>
    ${activeCommunityTab === 'channels' ? '<button class="btn sm" onclick="openCreateGroupModal()">+ Create Topic Channel</button>' : ''}
  </div>

  <div class="community-nav-tabs">
    <button class="community-nav-tab ${activeCommunityTab==='channels'?'active':''}" onclick="setCommunityTab('channels')">
      <span>💬 Community Channels (${rooms.length})</span>
    </button>
    <button class="community-nav-tab ${activeCommunityTab==='private'?'active':''}" onclick="setCommunityTab('private')">
      <span>🔒 Private Peer Messages (${convos.length})</span>
    </button>
  </div>

  ${isCreateGroupModalOpen ? renderCreateGroupModal() : ''}

  ${activeCommunityTab === 'channels' ? `
    <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(340px, 1fr));gap:20px;margin-top:16px;">
      ${rooms.length ? rooms.map(r => `
        <div class="card" style="display:flex;flex-direction:column;justify-content:space-between;border:1px solid var(--border-color);border-radius:16px;padding:20px;background:#fff;box-shadow:var(--shadow-sm);transition:all 0.2s ease;">
          <div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
              <h3 style="font-size:1.15rem;color:var(--text-primary);font-weight:700;">${r.name}</h3>
              <span class="pill" style="font-size:0.75rem;background:#e0f2fe;color:#0284c7;font-weight:700;">👥 ${r.member_count} Peers</span>
            </div>
            <p style="font-size:0.88rem;color:var(--text-secondary);line-height:1.5;margin-bottom:14px;min-height:42px;">${r.topic || 'Peer learning and collaborative skill exchange channel.'}</p>
            
            <div style="margin-bottom:14px;padding:10px;background:#f8fafc;border-radius:10px;">
              <div style="font-size:0.75rem;color:var(--text-dim);font-weight:600;margin-bottom:6px;text-transform:uppercase;">Channel Members</div>
              <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                ${r.members.slice(0, 5).map(m => `
                  <div class="user-avatar" style="width:28px;height:28px;font-size:0.72rem;" title="${m.name} (${m.email})">${getInitials(m.name)}</div>
                `).join('')}
                ${r.members.length > 5 ? `<span style="font-size:0.75rem;color:var(--text-dim);font-weight:600;">+${r.members.length - 5}</span>` : ''}
                <span style="font-size:0.8rem;color:var(--text-secondary);margin-left:auto;">Host: <strong>${r.creator_name}</strong></span>
              </div>
            </div>

            ${r.last_message ? `
              <div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:16px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                💬 <em>${r.last_message.sender_name}:</em> ${r.last_message.text}
              </div>
            ` : '<div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:16px;">💬 <em>No messages yet. Be the first to say hi!</em></div>'}
          </div>

          <div style="display:flex;gap:8px;">
            ${r.is_member ? `
              <button class="btn sm" style="width:100%" onclick="openGroupChat(${r.id})">Open Channel Chat 💬</button>
            ` : `
              <button class="btn secondary sm" style="flex:1" onclick="joinGroup(${r.id})">Join Channel 🚀</button>
              <button class="btn ghost sm" style="flex:1" onclick="openGroupChat(${r.id})">Preview Chat</button>
            `}
          </div>
        </div>
      `).join('') : '<div class="card" style="grid-column:1/-1;"><p class="empty">No community topic channels created yet. Be the first to launch one!</p></div>'}
    </div>
  ` : `
    <!-- Private Peer Messages Tab -->
    <div>
      ${convos.length ? convos.map(c => `
        <div class="private-peer-item" onclick="openChat(${c.session_id})">
          <div style="display:flex;align-items:center;gap:14px;flex:1;">
            <div class="user-avatar" style="width:44px;height:44px;font-size:1rem;">${getInitials(c.peer_name)}</div>
            <div style="flex:1;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:2px;flex-wrap:wrap;">
                <strong style="font-size:1rem;color:var(--text-primary);">${c.peer_name}</strong>
                ${c.peer_linkedin ? `<a href="${c.peer_linkedin}" target="_blank" class="linkedin-badge" onclick="event.stopPropagation()" title="Verified LinkedIn Profile">💼 in</a>` : ''}
                <span class="pill" style="font-size:0.72rem;background:#f1f5f9;color:var(--text-secondary);">${c.role}</span>
                <span style="font-size:0.75rem;font-weight:700;color:${c.session_status==='ACCEPTED'?'var(--accent-emerald)':c.session_status==='COMPLETED'||c.session_status==='CREDIT_RELEASED'?'var(--primary)':'var(--accent-amber)'}">
                  ● ${c.session_status}
                </span>
              </div>
              <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:4px;">
                Exchange: <strong>${c.skill_text}</strong>
              </div>
              <div style="font-size:0.8rem;color:var(--text-dim);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:550px;">
                ${c.last_message ? `💬 <em>${c.last_message.text}</em>` : 'No messages sent yet. Click to chat privately.'}
              </div>
            </div>
          </div>
          <div style="display:flex;gap:8px;align-items:center;" onclick="event.stopPropagation()">
            ${c.google_meet_url ? `
              <a href="${c.google_meet_url}" target="_blank" class="btn secondary sm" style="font-size:0.8rem;padding:6px 12px;">
                📹 Google Meet
              </a>
            ` : ''}
            <button class="btn sm" onclick="openChat(${c.session_id})">Private Chat 💬</button>
          </div>
        </div>
      `).join('') : `
        <div class="card" style="text-align:center;padding:40px;">
          <div style="font-size:2.5rem;margin-bottom:10px;">🔒</div>
          <h2>No Private Peer Conversations Yet</h2>
          <p class="sub" style="margin-bottom:16px;">When you propose, accept, or trade a skill with a peer from the Marketplace, your private 1-on-1 encrypted chat thread will appear here.</p>
          <button class="btn sm" onclick="go('home')">Browse Marketplace</button>
        </div>
      `}
    </div>
  `}
  `;
}

function renderCreateGroupModal() {
  const otherUsers = (allUsers || []).filter(u => u.id !== currentUser.id);
  return `
  <div class="card" style="border:2px solid var(--primary);margin-bottom:24px;background:#fdfdfd;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
      <h2>Create New Study Group</h2>
      <button class="btn ghost sm" onclick="closeCreateGroupModal()">✕ Cancel</button>
    </div>
    <p class="sub">Set up a shared group chatroom where multiple community peers can discuss skills and coordinate learning.</p>

    <div style="margin-bottom:14px;">
      <label>Group Room Name</label>
      <input id="grp_name" placeholder="e.g. 💻 Fullstack & AI Builders Circle">
    </div>

    <div style="margin-bottom:14px;">
      <label>Room Topic / Learning Focus</label>
      <input id="grp_topic" placeholder="e.g. Discussing React, Python ML models, and autonomous tool calling">
    </div>

    <div style="margin-bottom:18px;">
      <label>Invite Community Peers (Select multiple)</label>
      <div style="max-height:160px;overflow-y:auto;display:grid;grid-template-columns:repeat(auto-fill, minmax(200px, 1fr));gap:8px;padding:10px;background:#f8fafc;border-radius:10px;border:1px solid var(--border-color);">
        ${otherUsers.map(u => `
          <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;cursor:pointer;margin:0;font-weight:500;">
            <input type="checkbox" name="grp_members" value="${u.id}">
            <div class="user-avatar" style="width:24px;height:24px;font-size:0.65rem;">${getInitials(u.name)}</div>
            <span>${u.name}</span>
          </label>
        `).join('')}
      </div>
    </div>

    <div style="display:flex;gap:10px;">
      <button class="btn" onclick="createStudyGroup()">Launch Study Group Room</button>
      <button class="btn secondary" onclick="closeCreateGroupModal()">Cancel</button>
    </div>
  </div>
  `;
}

function openCreateGroupModal() { isCreateGroupModalOpen = true; render(); }
function closeCreateGroupModal() { isCreateGroupModalOpen = false; render(); }

async function createStudyGroup() {
  const name = document.getElementById('grp_name')?.value.trim();
  const topic = document.getElementById('grp_topic')?.value.trim();
  if (!name) { toast('Please enter a group name'); return; }

  const checkboxes = document.querySelectorAll('input[name="grp_members"]:checked');
  const memberIds = Array.from(checkboxes).map(cb => parseInt(cb.value, 10));

  try {
    const res = await api('/api/groups', {
      method: 'POST',
      body: JSON.stringify({
        name,
        topic,
        creator_id: currentUser.id,
        member_ids: memberIds
      })
    });
    isCreateGroupModalOpen = false;
    await refreshGroupRooms();
    toast(`Group "${name}" created with ${res.member_count} members!`);
    await openGroupChat(res.id);
  } catch (e) {
    toast('Failed to create group: ' + e.message);
  }
}

async function joinGroup(roomId) {
  try {
    await api(`/api/groups/${roomId}/join`, {
      method: 'POST',
      body: JSON.stringify({ user_id: currentUser.id })
    });
    await refreshGroupRooms();
    toast('Joined group study room!');
    await openGroupChat(roomId);
  } catch (e) {
    toast('Failed to join: ' + e.message);
  }
}

async function openGroupChat(roomId) {
  activeGroupRoomId = roomId;
  isInviteGroupModalOpen = false;
  try {
    const data = await api(`/api/groups/${roomId}/messages`);
    groupMessages = data.messages || [];
  } catch (e) {
    groupMessages = [];
  }
  go('group_chat');
}

function renderGroupChatPage() {
  if (!activeGroupRoomId) return '<div class="card"><p>No group room selected.</p></div>';
  const room = (groupRooms || []).find(r => r.id === activeGroupRoomId);
  if (!room) return '<div class="card"><p>Group room not found.</p><button class="btn sm" onclick="go(\'groups\')">Back</button></div>';

  const roomMemberIds = (room.members || []).map(m => m.id);
  const uninvitedPeers = (allUsers || []).filter(u => !roomMemberIds.includes(u.id));

  return `
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
    <div>
      <div style="display:flex;align-items:center;gap:10px;">
        <h1>${room.name}</h1>
        <span class="pill" style="background:#e0f2fe;color:#0284c7;font-weight:700;">👥 ${room.member_count} in Room</span>
      </div>
      <p class="sub" style="margin-bottom:0">${room.topic || 'Multi-peer study group & skill collaboration'}</p>
    </div>
    <div style="display:flex;gap:8px;">
      <button class="btn secondary sm" onclick="toggleInviteModal()">+ Invite Peer</button>
      <button class="btn ghost sm" onclick="openGroupRoomsView()">← Back to Groups</button>
    </div>
  </div>

  ${isInviteGroupModalOpen ? `
    <div class="card" style="border:1px solid var(--primary);margin-bottom:16px;background:#f8fafc;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <h3>Invite a Peer to ${room.name}</h3>
        <button class="btn ghost sm" onclick="toggleInviteModal()">✕</button>
      </div>
      ${uninvitedPeers.length ? `
        <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(220px, 1fr));gap:10px;">
          ${uninvitedPeers.map(u => `
            <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:#fff;border-radius:10px;border:1px solid var(--border-color);">
              <div style="display:flex;align-items:center;gap:8px;">
                <div class="user-avatar" style="width:28px;height:28px;font-size:0.75rem;">${getInitials(u.name)}</div>
                <div style="font-size:0.85rem;font-weight:600;">${u.name}</div>
              </div>
              <button class="btn sm" style="padding:4px 8px;font-size:0.75rem;" onclick="invitePeerToGroup(${u.id})">+ Add</button>
            </div>
          `).join('')}
        </div>
      ` : '<p style="font-size:0.85rem;color:var(--text-dim);margin:0">All community members are already in this study room!</p>'}
    </div>
  ` : ''}

  <div class="card" style="display:flex;flex-direction:column;height:calc(100vh - 230px);min-height:500px;padding:0;overflow:hidden;">
    <div style="padding:12px 18px;border-bottom:1px solid var(--border-color);display:flex;align-items:center;justify-content:space-between;background:#f8fafc;">
      <div style="display:flex;align-items:center;gap:8px;overflow-x:auto;">
        <span style="font-size:0.8rem;color:var(--text-secondary);font-weight:600;">Active Peers:</span>
        ${room.members.map(m => `
          <div class="user-avatar" style="width:26px;height:26px;font-size:0.7rem;" title="${m.name} (${m.email})">${getInitials(m.name)}</div>
        `).join('')}
      </div>
      <button class="btn ghost sm" style="font-size:0.8rem;" onclick="refreshGroupMessages()" title="Check for new messages">🔄 Refresh</button>
    </div>

    <div class="msgbox" id="groupMsgBox" style="flex:1;overflow-y:auto;padding:18px;">
      ${groupMessages.length ? groupMessages.map(m => {
        const isMe = m.sender_id === currentUser.id;
        return `
          <div class="msg ${isMe ? 'sent' : 'received'}" style="margin-bottom:12px;max-width:75%;">
            <div class="msg-author" style="font-size:0.75rem;margin-bottom:2px;font-weight:700;">
              ${isMe ? 'You' : m.sender_name}
            </div>
            <div style="font-size:0.92rem;line-height:1.45;">${m.text}</div>
          </div>
        `;
      }).join('') : '<div class="empty">No messages yet in this study room. Start the conversation!</div>'}
    </div>

    <div style="padding:14px 18px;border-top:1px solid var(--border-color);background:#fff;display:flex;gap:10px;">
      <input id="groupChatInput" placeholder="Message everyone in #${room.name}..." onkeydown="if(event.key==='Enter') sendGroupMsg()" style="margin:0;flex:1;">
      <button class="btn" style="flex:0 0 auto;" onclick="sendGroupMsg()">Send to Group</button>
    </div>
  </div>
  `;
}

function toggleInviteModal() {
  isInviteGroupModalOpen = !isInviteGroupModalOpen;
  render();
}

async function invitePeerToGroup(userId) {
  try {
    await api(`/api/groups/${activeGroupRoomId}/invite`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId })
    });
    await Promise.all([refreshGroupRooms(), refreshGroupMessages()]);
    toast('Peer added to study group!');
    render();
  } catch (e) {
    toast('Invite failed: ' + e.message);
  }
}

async function refreshGroupMessages() {
  if (!activeGroupRoomId) return;
  try {
    const data = await api(`/api/groups/${activeGroupRoomId}/messages`);
    groupMessages = data.messages || [];
    render();
    setTimeout(() => {
      const box = document.getElementById('groupMsgBox');
      if (box) box.scrollTop = box.scrollHeight;
    }, 50);
  } catch (e) { }
}

async function sendGroupMsg() {
  const input = document.getElementById('groupChatInput');
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  try {
    await api(`/api/groups/${activeGroupRoomId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ sender_id: currentUser.id, text })
    });
    input.value = '';
    await refreshGroupMessages();
  } catch (e) {
    toast('Send failed: ' + e.message);
  }
}

/* ---------- ACCOUNT ---------- */
function renderAccount() {
  const teach = currentUser?.teach_listings || [];
  const learn = currentUser?.learn_listings || [];
  return `
  <h1>Account Overview</h1>
  <p class="sub">View your member profile, MG Coin activity, and personal stats.</p>
  <div class="card" style="display:flex;align-items:center;gap:24px;">
    <div class="user-avatar" style="width:72px;height:72px;font-size:1.8rem;box-shadow:var(--shadow-md);">${getInitials(currentUser.name)}</div>
    <div>
      <h2 style="margin-bottom:4px">${currentUser.name}</h2>
      <p style="color:var(--text-secondary);font-size:0.92rem;margin-bottom:6px">${currentUser.email}</p>
      <span class="mg-coin-pill">🪙 ${currentUser.balance} Available MG Coins</span>
    </div>
  </div>
  <div class="row">
    <div class="card" style="text-align:center;"><h2 style="font-size:2rem;color:var(--primary);margin-bottom:4px">${teach.length}</h2><p class="sub" style="margin:0">Skills Offered</p></div>
    <div class="card" style="text-align:center;"><h2 style="font-size:2rem;color:var(--accent-coral);margin-bottom:4px">${learn.length}</h2><p class="sub" style="margin:0">Learning Goals</p></div>
    <div class="card" style="text-align:center;"><h2 style="font-size:2rem;color:var(--accent-amber);margin-bottom:4px">🪙 ${currentUser.balance}</h2><p class="sub" style="margin:0">MG Coins</p></div>
  </div>
  <div class="card">
    <h2>Bio Summary</h2>
    <p style="color:var(--text-secondary);">${currentUser.bio || 'No bio written yet.'}</p>
    <button class="btn secondary sm" style="margin-top:14px" onclick="go('profile')">Edit Profile Bio</button>
  </div>`;
}

/* ---------- SETTINGS ---------- */
function renderSettings() {
  return `
  <h1>Settings & Preferences</h1>
  <p class="sub">Customize your experience and notification settings.</p>
  <div class="card">
    <h2>Notifications & Alerts</h2>
    <div class="setting-row"><div><strong style="color:var(--text-primary)">Email Session Notifications</strong><p style="font-size:0.85rem;color:var(--text-dim)">Receive email alerts when a peer requests or accepts a session.</p></div>
      <label class="toggle-switch"><input type="checkbox" checked><span class="toggle-slider"></span></label></div>
    <div class="setting-row"><div><strong style="color:var(--text-primary)">Public Profile Bio</strong><p style="font-size:0.85rem;color:var(--text-dim)">Allow community members to view your bio on match cards.</p></div>
      <label class="toggle-switch"><input type="checkbox" checked><span class="toggle-slider"></span></label></div>
  </div>
  <div class="card" style="border-color:#fecdd3;">
    <h2 style="color:var(--accent-coral)">Account Session</h2>
    <p class="sub">Log out of your current session on this device.</p>
    <button class="btn" style="background:var(--accent-coral)" onclick="logout()">Log Out Now</button>
  </div>`;
}

/* ---------- DASHBOARD (FREE SKILLS TRACKS) ---------- */
function setCatTab(tab) { activeCatTab = tab; render(); }

function renderDashboard() {
  const filtered = TRENDING_CATALOGUE.filter(i => activeCatTab === 'all' || i.category === activeCatTab);
  const userCerts = currentUser?.certifications || [];

  return `
  <div style="margin-bottom:28px;">
    <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:14px;flex-wrap:wrap;gap:12px;">
      <div>
        <h1 style="display:flex;align-items:center;gap:10px;">🎁 Free Trending Skills Tracks</h1>
        <p class="sub" style="margin-bottom:0">Complete free crash courses to earn <strong>🪙 +2 MG Coins</strong> and unlock domain instructor certification to teach on MOGG.</p>
      </div>
      <div style="display:flex;gap:8px;align-items:center;">
        <span style="font-size:0.82rem;color:var(--text-secondary);font-weight:600;">Your Certified Domains:</span>
        <span class="badge" style="background:#ecfdf5;color:#047857;border:1px solid #a7f3d0;font-weight:700;">
          ${userCerts.length} / 6 Domains
        </span>
      </div>
    </div>

    <div class="filter-tabs">
      <button class="filter-tab ${activeCatTab==='all'?'active':''}" onclick="setCatTab('all')">All Trending Tracks (${TRENDING_CATALOGUE.length})</button>
      <button class="filter-tab ${activeCatTab==='tech'?'active':''}" onclick="setCatTab('tech')">💻 Tech</button>
      <button class="filter-tab ${activeCatTab==='soft'?'active':''}" onclick="setCatTab('soft')">🗣️ Soft Skills</button>
      <button class="filter-tab ${activeCatTab==='survival'?'active':''}" onclick="setCatTab('survival')">🏕️ Survival</button>
      <button class="filter-tab ${activeCatTab==='creative'?'active':''}" onclick="setCatTab('creative')">🎨 Creative</button>
      <button class="filter-tab ${activeCatTab==='languages'?'active':''}" onclick="setCatTab('languages')">🗣️ Languages</button>
      <button class="filter-tab ${activeCatTab==='business'?'active':''}" onclick="setCatTab('business')">💼 Business</button>
    </div>

    <div class="catalogue-grid">
      ${filtered.map(item => {
        const isCertified = userCerts.includes(item.category);
        return `
        <div class="catalogue-card">
          <div>
            <div class="cat-header">
              <span class="cat-badge ${item.category}">${item.categoryLabel}</span>
              <span class="cat-meta">${item.difficulty} • ${item.duration}</span>
            </div>
            <div class="cat-title">${item.title}</div>
            <div class="cat-box"><strong>⚙️ What you'll master:</strong><br>${item.description}</div>
            <div style="margin:10px 0 6px;">
              ${isCertified ? `
                <span class="domain-cert-badge" style="font-size:0.75rem;padding:3px 8px;">
                  ✅ Certified Instructor in ${getDomainLabel(item.category)}
                </span>
              ` : `
                <span style="font-size:0.75rem;background:#fef3c7;color:#92400e;padding:3px 8px;border-radius:10px;font-weight:600;">
                  🪙 +2 MG Coins on Course Quiz
                </span>
              `}
            </div>
          </div>
          <div>
            <div style="margin-bottom:12px;">${item.tags.map(t => `<span class="pill" style="font-size:0.75rem">${t}</span>`).join('')}</div>
            <div class="cat-footer" style="flex-wrap:wrap;gap:6px;">
              <button class="btn sm" style="width:100%;margin-bottom:4px;background:${isCertified ? 'var(--bg-surface)' : 'var(--primary)'};color:${isCertified ? 'var(--text-primary)' : '#fff'};border:${isCertified ? '1px solid var(--border-color)' : 'none'};" onclick="openCourseModal('${item.category}')">
                ${isCertified ? '🎓 Review Course & Syllabus' : '🎓 Take Course & Quiz (+2 Coins)'}
              </button>
              <button class="btn secondary sm" style="flex:1" onclick="addLearnGoal('${item.title.replace(/'/g, "\\'")}')">+ Learn Goal</button>
              <button class="btn secondary sm" style="flex:1" onclick="searchTeachers('${item.title.replace(/'/g, "\\'")}')">Find Peers</button>
            </div>
          </div>
        </div>
      `;
      }).join('')}
    </div>
  </div>`;
}

async function addLearnGoal(skillTitle) {
  try {
    await api('/api/listings', {
      method: 'POST',
      body: JSON.stringify({
        user_id: currentUser.id,
        type: 'LEARN',
        skill_text: skillTitle,
        category: 'General',
        domain: 'tech',
        fee_text: 'Free Peer Exchange',
        description: `Goal to master: ${skillTitle}`
      })
    });
    await refreshCurrentUser();
    toast(`Added "${skillTitle}" to your learning goals!`);
  } catch (e) { toast('Failed: ' + e.message); }
}

async function searchTeachers(skillTitle) {
  try {
    const data = await api(`/api/teachers?skill=${encodeURIComponent(skillTitle)}&user_id=${currentUser.id}`);
    if (data.teachers && data.teachers.length > 0) {
      toast(`Found ${data.count} matching teachers for "${skillTitle}"! Check the Marketplace.`);
    } else {
      toast(`No exact teacher matches found for "${skillTitle}" yet.`);
    }
    go('home');
  } catch (e) { toast('Search failed: ' + e.message); }
}

/* ---------- SKILLBOT AI TUTOR VIEW ---------- */
function setAiContext(ctx) {
  aiTutorSkillContext = ctx;
  render();
}

function askAiQuickPrompt(promptText) {
  const inp = document.getElementById('ai_query_input');
  if (inp) {
    inp.value = promptText;
    sendAiTutorQuery();
  }
}

async function sendAiTutorQuery() {
  const inp = document.getElementById('ai_query_input');
  if (!inp) return;
  const q = inp.value.trim();
  if (!q) return;

  aiTutorHistory.push({ role: 'user', content: q });
  inp.value = '';
  isAiTutorLoading = true;
  render();

  try {
    const data = await api('/api/ai/ask', {
      method: 'POST',
      body: JSON.stringify({
        query: q,
        skill_context: aiTutorSkillContext,
        chat_history: aiTutorHistory.slice(-6)
      })
    });
    aiTutorHistory.push({ role: 'assistant', content: data.reply || 'No response generated.' });
  } catch (err) {
    aiTutorHistory.push({ role: 'assistant', content: '⚠️ Error querying AI Tutor: ' + err.message });
  } finally {
    isAiTutorLoading = false;
    render();
    const chatContainer = document.getElementById('ai-chat-messages');
    if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
  }
}

function renderAiTutor() {
  const contexts = ['React', 'Python', 'Linear Algebra', 'Public Speaking', 'UI/UX Design', 'General'];
  
  const messagesHtml = aiTutorHistory.map(m => {
    const isBot = m.role === 'assistant';
    const formatted = m.content
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return `
      <div style="display:flex;gap:12px;margin-bottom:16px;align-items:flex-start;justify-content:${isBot ? 'flex-start' : 'flex-end'};">
        ${isBot ? '<div class="user-avatar" style="background:var(--primary);color:#fff;width:38px;height:38px;border-radius:12px;font-size:1.1rem;flex-shrink:0;">🤖</div>' : ''}
        <div style="max-width:78%;padding:14px 18px;border-radius:${isBot ? '4px 18px 18px 18px' : '18px 4px 18px 18px'};background:${isBot ? 'var(--bg-surface)' : 'var(--primary)'};color:${isBot ? 'var(--text-primary)' : '#ffffff'};border:${isBot ? '1px solid var(--border-color)' : 'none'};box-shadow:var(--shadow-sm);line-height:1.6;font-size:0.95rem;">
          ${formatted}
        </div>
        ${!isBot ? `<div class="user-avatar" style="width:38px;height:38px;border-radius:12px;font-size:0.9rem;flex-shrink:0;">${getInitials(currentUser.name)}</div>` : ''}
      </div>
    `;
  }).join('');

  return `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:10px;">
      <div>
        <h1 style="display:flex;align-items:center;gap:10px;">🤖 SkillBot AI Peer Tutor</h1>
        <p class="sub" style="margin-bottom:0;">Ask doubts, get study roadmaps, and generate peer prep exercises. Works 100% offline & venue-proof!</p>
      </div>
      <span class="badge" style="background:rgba(16,185,129,0.12);color:var(--accent-emerald);border:1px solid rgba(16,185,129,0.3);padding:6px 14px;border-radius:20px;font-weight:600;font-size:0.85rem;">
        ⚡ Instant Local Fallback Active
      </span>
    </div>

    <!-- Skill Context Selector -->
    <div class="card" style="margin-bottom:16px;padding:12px 18px;">
      <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
        <span style="font-size:0.88rem;font-weight:600;color:var(--text-secondary);">Learning Subject Context:</span>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          ${contexts.map(c => `
            <button class="pill-btn ${aiTutorSkillContext === c ? 'active' : ''}" onclick="setAiContext('${c}')" style="cursor:pointer;padding:4px 12px;border-radius:16px;font-size:0.84rem;border:1px solid var(--border-color);background:${aiTutorSkillContext === c ? 'var(--primary)' : 'transparent'};color:${aiTutorSkillContext === c ? '#fff' : 'var(--text-secondary)'}">
              ${c}
            </button>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- Chat Messages Window -->
    <div class="card" id="ai-chat-messages" style="height:420px;overflow-y:auto;background:var(--bg-surface-hover);padding:20px;margin-bottom:16px;">
      ${messagesHtml}
      ${isAiTutorLoading ? `
        <div style="display:flex;gap:12px;align-items:center;margin-bottom:16px;">
          <div class="user-avatar" style="background:var(--primary);color:#fff;width:38px;height:38px;border-radius:12px;font-size:1.1rem;">🤖</div>
          <div style="padding:10px 16px;border-radius:4px 18px 18px 18px;background:var(--bg-surface);border:1px solid var(--border-color);font-size:0.9rem;color:var(--text-dim);">
            SkillBot is thinking & preparing your guidance...
          </div>
        </div>
      ` : ''}
    </div>

    <!-- Suggested Quick Prompts -->
    <div style="display:flex;gap:8px;margin-bottom:12px;overflow-x:auto;padding-bottom:4px;">
      <button class="pill-btn" onclick="askAiQuickPrompt('Explain key concept intuition simply')" style="font-size:0.8rem;background:var(--bg-surface);border:1px solid var(--border-color);color:var(--text-dim);cursor:pointer;white-space:nowrap;padding:6px 12px;border-radius:14px;">💡 Explain concept simply</button>
      <button class="pill-btn" onclick="askAiQuickPrompt('Give me 3 practice exercises for my peer session')" style="font-size:0.8rem;background:var(--bg-surface);border:1px solid var(--border-color);color:var(--text-dim);cursor:pointer;white-space:nowrap;padding:6px 12px;border-radius:14px;">🎯 3 Peer Practice Drills</button>
      <button class="pill-btn" onclick="askAiQuickPrompt('What are common interview questions on this?')" style="font-size:0.8rem;background:var(--bg-surface);border:1px solid var(--border-color);color:var(--text-dim);cursor:pointer;white-space:nowrap;padding:6px 12px;border-radius:14px;">❓ Common Interview Doubts</button>
    </div>

    <!-- Input Form -->
    <div style="display:flex;gap:10px;">
      <input id="ai_query_input" placeholder="Type your doubt or question (e.g. 'Explain React hooks' or 'Linear algebra intuition')..." style="flex:1;" onkeydown="if(event.key==='Enter') sendAiTutorQuery()">
      <button class="btn" onclick="sendAiTutorQuery()" style="min-width:140px;display:flex;align-items:center;justify-content:center;gap:6px;">
        <span>Ask SkillBot</span> 🚀
      </button>
    </div>
  `;
}

/* ---------- FREE COURSE & QUIZ MODAL ---------- */
function renderCourseModal() {
  if (!activeCourseModal) return '';
  const c = activeCourseModal;
  const isCertified = (currentUser?.certifications || []).includes(c.domain);
  const quiz = c.quiz || [];

  return `
  <div class="modal-backdrop" onclick="closeCourseModal()">
    <div class="modal-card" onclick="event.stopPropagation()">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;gap:12px;">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap;">
            <span class="domain-tag ${c.domain}">${getDomainLabel(c.domain)}</span>
            <span class="pill" style="font-size:0.75rem;background:#e0f2fe;color:#0284c7;font-weight:700;">⏱️ ${c.duration}</span>
            ${isCertified ? '<span class="domain-cert-badge">✅ Certified</span>' : '<span class="fee-pill mg" style="font-size:0.75rem;">🪙 Earn +2 MG Coins</span>'}
          </div>
          <h2 style="font-size:1.35rem;color:var(--text-primary);margin:0;">${c.title}</h2>
        </div>
        <button class="btn ghost sm" onclick="closeCourseModal()" style="font-size:1.2rem;line-height:1;padding:4px 10px;">✕</button>
      </div>

      <div style="background:#f8fafc;border:1px solid var(--border-color);border-radius:12px;padding:16px;margin-bottom:20px;">
        <h3 style="font-size:0.95rem;margin-bottom:8px;color:var(--text-primary);">📖 Course Syllabus & Curriculum</h3>
        <p style="font-size:0.88rem;color:var(--text-secondary);line-height:1.6;margin-bottom:12px;">${c.summary}</p>
        <div style="font-size:0.82rem;font-weight:700;color:var(--text-primary);margin-bottom:6px;">Key Curriculum Takeaways:</div>
        <ul style="margin:0;padding-left:18px;font-size:0.84rem;color:var(--text-secondary);line-height:1.6;">
          ${(c.takeaways || []).map(t => `<li>${t}</li>`).join('')}
        </ul>
      </div>

      <div style="border-top:1px solid var(--border-color);padding-top:16px;margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
          <h3 style="font-size:1.05rem;color:var(--text-primary);margin:0;">📝 Domain Competency Assessment</h3>
          <span style="font-size:0.8rem;color:var(--text-dim);">Score 100% to certify & teach</span>
        </div>
        <p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:16px;">
          Pass both questions correctly to earn your verified domain certification badge and unlock teaching listings in <strong>${getDomainLabel(c.domain)}</strong>.
        </p>

        ${quiz.map((qItem, qIdx) => `
          <div style="margin-bottom:16px;background:#ffffff;border:1px solid var(--border-color);border-radius:12px;padding:14px;">
            <div style="font-weight:700;font-size:0.9rem;color:var(--text-primary);margin-bottom:10px;">
              Question ${qIdx + 1}: ${qItem.q}
            </div>
            <div style="display:flex;flex-direction:column;gap:6px;">
              ${qItem.options.map((opt, optIdx) => {
                const isSelected = activeQuizAnswers[qIdx] === optIdx;
                return `
                  <div class="quiz-option-card ${isSelected ? 'selected' : ''}" onclick="selectQuizOption(${qIdx}, ${optIdx})">
                    <input type="radio" name="quiz_q_${qIdx}" ${isSelected ? 'checked' : ''} style="margin:0;cursor:pointer;flex-shrink:0;">
                    <span style="font-size:0.86rem;color:var(--text-primary);line-height:1.4;">${opt}</span>
                  </div>
                `;
              }).join('')}
            </div>
          </div>
        `).join('')}
      </div>

      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;border-top:1px solid var(--border-color);padding-top:16px;">
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:1.1rem;">🪙</span>
          <span style="font-size:0.85rem;color:var(--text-secondary);">Reward upon passing: <strong>+2 MG Coins</strong></span>
        </div>
        <div style="display:flex;gap:10px;">
          <button class="btn secondary sm" onclick="closeCourseModal()">Cancel</button>
          <button class="btn sm" onclick="submitCourseQuiz()">Submit Assessment & Certify 🎓</button>
        </div>
      </div>
    </div>
  </div>
  `;
}

/* ---------- RENDER CONTROLLER ---------- */
function render() {
  renderHeader();
  renderSidebar();

  const app = document.getElementById('app');
  if (!app) return;
  if (view === 'login') { app.innerHTML = renderLogin(); return; }
  if (!currentUser) { view = 'login'; app.innerHTML = renderLogin(); return; }

  let html = '';
  if (view === 'home') html = renderHomePage();
  else if (view === 'dashboard') html = renderDashboard();
  else if (view === 'profile') html = renderProfile();
  else if (view === 'skill_detail') html = renderSkillDetailPage();
  else if (view === 'add_skill') html = renderAddSkillPage();
  else if (view === 'requests') html = renderRequests();
  else if (view === 'community' || view === 'groups') html = renderCommunityPage();
  else if (view === 'group_chat') html = renderGroupChatPage();
  else if (view === 'ai_tutor') html = renderAiTutor();
  else if (view === 'account') html = renderAccount();
  else if (view === 'settings') html = renderSettings();
  else if (view === 'chat') html = renderChat();
  else html = renderHomePage();

  if (activeCourseModal) {
    html += renderCourseModal();
  }

  app.innerHTML = html;
}

// Initial render — login page
render();
