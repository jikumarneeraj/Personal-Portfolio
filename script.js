/* ==========================================================================
   AI/ML CAREER PORTFOLIO - INTERACTIVE LOGIC & DATA (NEERAJ KUMAR)
   ========================================================================== */

// 1. Projects Database
const projectsData = [
  {
    id: "amrit-pharmacy",
    title: "AMRIT Pharmacy Optimization",
    category: "data-science",
    desc: "Analyzed 56K+ sales records using Python to identify demand trends, ABC inventory segments, and revenue drivers, proposing data-driven inventory and operational improvements for KGMU Lucknow.",
    tags: ["Python", "Pandas", "NumPy", "Data Analysis", "ABC Analysis"],
    link: "https://github.com/jikumarneeraj/Service-and-Operational-Optimization-of-AMRIT-Pharmacy-at-KGMU",
    linkLabel: "GitHub Repo"
  },
  {
    id: "kidney-disease",
    title: "Kidney Disease Classification",
    category: "ml-nlp",
    desc: "Engineered an end-to-end deep learning classification pipeline using CNNs (VGG16) to categorize kidney CT scans. Integrated DVC for data version tracking, MLflow for training runs, and Docker for deployment.",
    tags: ["Python", "Deep Learning", "CNN", "MLflow", "DVC", "Docker"],
    link: "https://github.com/jikumarneeraj/Kidney-Disease-Classification",
    linkLabel: "GitHub Repo"
  },
  {
    id: "comment-prediction",
    title: "Comment Category Prediction",
    category: "ml-nlp",
    desc: "Developed a text classification pipeline using Python and NLP techniques. Preprocessed user comments and trained models to classify them into distinct categories with high validation accuracy.",
    tags: ["Python", "NLP", "Scikit-Learn", "NLTK", "Text Mining"],
    link: "https://www.kaggle.com/competitions/comment-category-prediction-challenge/overview",
    linkLabel: "Kaggle Challenge"
  },
  {
    id: "survival-detection",
    title: "Survival Detection (ML)",
    category: "ml-nlp",
    desc: "Engineered a predictive machine learning classifier in Python to evaluate passenger details (demographics, boarding class) and estimate survival likelihood, optimizing model parameters via cross-validation.",
    tags: ["Python", "Scikit-Learn", "Machine Learning", "Classification"],
    link: "https://www.kaggle.com/competitions/survival-detection/overview",
    linkLabel: "Kaggle Challenge"
  },
  {
    id: "cost-dashboard",
    title: "IT & Business Cost Dashboard",
    category: "data-science",
    desc: "Designed and implemented an interactive Power BI dashboard to analyze and monitor IT and corporate costs across various scenarios, regions, cost centers, and timelines.",
    tags: ["Power BI", "Excel", "Data Modeling", "Business Intelligence"],
    link: "https://drive.google.com/drive/folders/1uu-IKaIeoqb-fPW-SN5Z71O_G2DJJhcD",
    linkLabel: "Google Drive Folder"
  },
  {
    id: "quiz-master",
    title: "Quiz Master Web Platform",
    category: "software",
    desc: "Built a production-grade full-stack quiz management system featuring role-based access, REST APIs, background job dispatching, and cache optimization.",
    tags: ["Flask", "Vue.js", "SQLite", "Redis", "Celery", "REST API"],
    link: "https://github.com/23f2002096/quiz_master_v2",
    linkLabel: "GitHub Repo"
  },
  {
    id: "whatsapp-chat",
    title: "WhatsApp Chat Analyzer",
    category: "data-science",
    desc: "Developed a web-based data dashboard using Python and Flask that parses exported WhatsApp chat logs to render metrics, chat frequencies, and active participant timelines.",
    tags: ["Python", "Flask", "Pandas", "Matplotlib", "Text Processing"],
    link: "https://github.com/jikumarneeraj/whatsapp_chat_analyzer",
    linkLabel: "GitHub Repo"
  },
  {
    id: "weather-assistant",
    title: "Voice Weather Assistant",
    category: "software",
    desc: "Built an interactive voice-activated weather utility in Python that fetches live weather metrics via WeatherAPI and communicates forecasts using text-to-speech synthesis.",
    tags: ["Python", "Web APIs", "TTS Engine", "Voice Interaction"],
    link: "https://github.com/jikumarneeraj/weather_mini_project",
    linkLabel: "GitHub Repo"
  },
  {
    id: "water-reminder",
    title: "Desktop Hydration Reminder",
    category: "software",
    desc: "Created a background notification assistant in Python that triggers scheduled reminders, promoting healthy work habits via native desktop alerts.",
    tags: ["Python", "Windows API", "Scheduling", "Desktop Utilities"],
    link: "https://github.com/jikumarneeraj/drink_water_reminder",
    linkLabel: "GitHub Repo"
  }
];

// 2. DOM Elements Selection
document.addEventListener("DOMContentLoaded", () => {
  // Navigation elements
  const mainHeader = document.getElementById("main-header");
  const mobileNavToggle = document.getElementById("mobile-nav-toggle");
  const navMenu = document.getElementById("nav-menu");
  const navLinks = document.querySelectorAll(".nav-link");

  // Project sections
  const projectsContainer = document.getElementById("projects-container");
  const filterBtns = document.querySelectorAll(".filter-btn");

  // Skills progress elements
  const skillBars = document.querySelectorAll(".skill-progress");
  const skillsSection = document.getElementById("skills");

  // AI Training Simulator elements
  const btnTrain = document.getElementById("btn-train");
  const trainingStatus = document.getElementById("training-status");
  const paramLr = document.getElementById("param-lr");
  const lrVal = document.getElementById("lr-val");
  const paramOptimizer = document.getElementById("param-optimizer");
  const paramEpochs = document.getElementById("param-epochs");
  
  const metricEpoch = document.getElementById("metric-epoch");
  const metricLoss = document.getElementById("metric-loss");
  const metricAcc = document.getElementById("metric-acc");
  const metricLr = document.getElementById("metric-lr");
  
  const pathLoss = document.getElementById("path-loss");
  const pathAcc = document.getElementById("path-acc");
  
  // Neural Console / Terminal elements
  const neuralInterface = document.getElementById("neural-interface");
  const terminalScreen = document.getElementById("terminal-screen");
  const terminalForm = document.getElementById("terminal-form");
  const terminalInput = document.getElementById("terminal-input");
  const presetBtns = document.querySelectorAll(".preset-btn");

  // Contact Form elements
  const contactForm = document.getElementById("contact-form");
  const formFeedback = document.getElementById("form-feedback");

  // ==========================================
  // NAVIGATION LOGIC
  // ==========================================

  // Sticky header background transition
  window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
      mainHeader.classList.add("scrolled");
    } else {
      mainHeader.classList.remove("scrolled");
    }
    highlightActiveNavLink();
  });

  // Mobile navigation menu toggle
  mobileNavToggle.addEventListener("click", () => {
    navMenu.classList.toggle("open");
    const isOpen = navMenu.classList.contains("open");
    mobileNavToggle.innerHTML = isOpen ? '<i class="fa-solid fa-xmark"></i>' : '<i class="fa-solid fa-bars"></i>';
  });

  // Close mobile nav on link click
  navLinks.forEach(link => {
    link.addEventListener("click", () => {
      navMenu.classList.remove("open");
      mobileNavToggle.innerHTML = '<i class="fa-solid fa-bars"></i>';
    });
  });

  // Auto-highlight active navigation link during scroll
  function highlightActiveNavLink() {
    let scrollPosition = window.scrollY + 100;
    
    document.querySelectorAll("section[id]").forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      const sectionId = section.getAttribute("id");
      
      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        navLinks.forEach(link => {
          link.classList.remove("active");
          if (link.getAttribute("href") === `#${sectionId}`) {
            link.classList.add("active");
          }
        });
      }
    });
  }

  // ==========================================
  // PROJECTS RENDER & FILTER LOGIC
  // ==========================================

  function renderProjects(categoryFilter = "all") {
    projectsContainer.innerHTML = "";
    
    const filteredProjects = projectsData.filter(proj => {
      if (categoryFilter === "all") return true;
      return proj.category === categoryFilter;
    });

    filteredProjects.forEach(proj => {
      // Determine proper folder icon based on category
      let categoryIcon = "fa-folder-open";
      if (proj.category === "ml-nlp") categoryIcon = "fa-brain";
      else if (proj.category === "data-science") categoryIcon = "fa-chart-simple";
      else if (proj.category === "software") categoryIcon = "fa-server";

      const card = document.createElement("a");
      card.href = proj.link;
      card.target = "_blank";
      card.rel = "noopener noreferrer";
      card.className = "project-card glass glow-card";
      card.innerHTML = `
        <div class="project-card-body">
          <div class="project-card-header">
            <h3>${proj.title}</h3>
            <div class="project-icon"><i class="fa-solid ${categoryIcon}"></i></div>
          </div>
          <p class="project-desc">${proj.desc}</p>
          <div class="project-tags">
            ${proj.tags.map(tag => `<span class="project-tag">${tag}</span>`).join("")}
          </div>
          <div class="project-links">
            <span><i class="fa-solid fa-link"></i> ${proj.linkLabel}</span>
            <span style="margin-left: auto;"><i class="fa-solid fa-arrow-up-right-from-square"></i></span>
          </div>
        </div>
      `;
      projectsContainer.appendChild(card);
    });
  }

  // Initial projects render
  renderProjects();

  // Project filter buttons click handler
  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      filterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      
      const filterValue = btn.getAttribute("data-filter");
      renderProjects(filterValue);
    });
  });

  // ==========================================
  // SKILLS PROGRESS ANIMATION
  // ==========================================

  // Animate skill bars when they enter viewport
  const skillsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        skillBars.forEach(bar => {
          // Read target width directly from inline styles parsed by browser (handles semicolons automatically)
          const targetWidth = bar.style.width || "0%";
          bar.style.width = "0";
          setTimeout(() => {
            bar.style.width = targetWidth;
          }, 100);
        });
        // Unobserve after running animation once
        skillsObserver.unobserve(skillsSection);
      }
    });
  }, { threshold: 0.15 });

  if (skillsSection) {
    skillsObserver.observe(skillsSection);
  }

  // ==========================================
  // AI MODEL TRAINING SIMULATOR
  // ==========================================

  // Sync hyperparameter slider value text
  paramLr.addEventListener("input", (e) => {
    lrVal.textContent = parseFloat(e.target.value).toFixed(4);
  });

  let isTraining = false;

  btnTrain.addEventListener("click", async () => {
    if (isTraining) return;
    
    isTraining = true;
    btnTrain.disabled = true;
    btnTrain.innerHTML = '<i class="fa-solid fa-sync fa-spin"></i> Training in Progress...';
    
    // Clear terminal screen if unlocked previously
    if (neuralInterface.classList.contains("unlocked")) {
      neuralInterface.classList.remove("unlocked");
      neuralInterface.classList.add("locked");
      terminalScreen.innerHTML = `
        <div class="terminal-line">Neeraj-Bot neural network reset.</div>
        <div class="terminal-line">Parameters locked. Waiting for retraining...</div>
      `;
    }

    // Read hyperparams
    const lr = parseFloat(paramLr.value);
    const targetEpochs = parseInt(paramEpochs.value) || 10;
    const optimizer = paramOptimizer.options[paramOptimizer.selectedIndex].text;

    // Set UI states
    trainingStatus.className = "status-indicator training";
    trainingStatus.textContent = "Status: TRAINING";
    metricLr.textContent = lr.toFixed(4);

    // Reset charts paths
    pathLoss.setAttribute("d", "");
    pathAcc.setAttribute("d", "");

    // Training progression calculations
    const lossPoints = [];
    const accPoints = [];
    
    let currentLoss = 2.45; // Start with high loss
    let currentAcc = 0.32;  // Start with low accuracy (random guessing)

    // Chart Dimensions
    // SVG viewBox: 0 0 400 150
    // Chart plot boundary: X [40, 380], Y [20, 120]
    const chartWidth = 340; 
    const chartHeight = 100;
    const startX = 40;
    const startY = 120; // Bottom (Y=120 corresponds to value 0.0, Y=20 corresponds to value 1.0)

    function mapValueToY(val, maxVal = 1.0) {
      // Linear mapping to chart Y space [20, 120]
      // val = 0 -> Y = 120
      // val = maxVal -> Y = 20
      const ratio = Math.min(Math.max(val / maxVal, 0), 1);
      return startY - (ratio * chartHeight);
    }

    // Run epochs simulation
    for (let epoch = 1; epoch <= targetEpochs; epoch++) {
      // Simulate epoch step duration
      await new Promise(resolve => setTimeout(resolve, 400));
      
      // Calculate learning convergence behavior
      // Higher learning rates converge faster but can fluctuate
      const rateFactor = lr * 250; 
      const noise = (Math.random() - 0.5) * 0.08;
      
      // Compute Loss decrease
      currentLoss = currentLoss - (currentLoss * (0.22 + noise * 0.1) * (1 + rateFactor * 0.05));
      if (currentLoss < 0.05) currentLoss = 0.05;

      // Compute Val Accuracy increase
      const remainingAcc = 1.0 - currentAcc;
      currentAcc = currentAcc + (remainingAcc * (0.28 + noise * 0.08) * (1 + rateFactor * 0.03));
      if (currentAcc > 0.998) currentAcc = 0.998;

      // UI updates
      metricEpoch.textContent = `${epoch}/${targetEpochs}`;
      metricLoss.textContent = currentLoss.toFixed(4);
      metricAcc.textContent = `${(currentAcc * 100).toFixed(2)}%`;

      // Map coordinates
      const x = startX + ((epoch - 1) / (targetEpochs - 1)) * chartWidth;
      
      // Map Loss (max value of 2.5)
      const lossY = mapValueToY(currentLoss, 2.5);
      // Map Accuracy (max value of 1.0)
      const accY = mapValueToY(currentAcc, 1.0);

      lossPoints.push({ x, y: lossY });
      accPoints.push({ x, y: accY });

      // Rebuild paths
      let dLoss = `M ${lossPoints[0].x} ${lossPoints[0].y}`;
      let dAcc = `M ${accPoints[0].x} ${accPoints[0].y}`;

      for (let i = 1; i < lossPoints.length; i++) {
        dLoss += ` L ${lossPoints[i].x} ${lossPoints[i].y}`;
        dAcc += ` L ${accPoints[i].x} ${accPoints[i].y}`;
      }

      pathLoss.setAttribute("d", dLoss);
      pathAcc.setAttribute("d", dAcc);
    }

    // Training Complete
    trainingStatus.className = "status-indicator complete";
    trainingStatus.textContent = "Status: CONVERGED";
    btnTrain.disabled = false;
    btnTrain.innerHTML = '<i class="fa-solid fa-check"></i> Retrain Model';
    isTraining = false;

    // Unlock neural interface console
    unlockTerminal(optimizer, targetEpochs, lr, currentAcc, currentLoss);
  });

  // ==========================================
  // NEURAL CONSOLE / TERMINAL INTERACTIVES
  // ==========================================

  function unlockTerminal(opt, epochs, lr, finalAcc, finalLoss) {
    neuralInterface.classList.remove("locked");
    neuralInterface.classList.add("unlocked");
    
    // Smooth scroll down to console
    setTimeout(() => {
      neuralInterface.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 200);

    // Boot sequence prints
    terminalScreen.innerHTML = "";
    
    const bootLines = [
      `Initializing weights from AdamW checkpoint... [OK]`,
      `Model parameters: optimizer=${opt}, LR=${lr.toFixed(4)}, epochs=${epochs}`,
      `Validation accuracy achieved: ${(finalAcc * 100).toFixed(2)}%`,
      `Final validation loss: ${finalLoss.toFixed(4)}`,
      `Neeraj-Bot predictive engine loaded.`,
      `Type 'help' to see active query triggers.`
    ];

    let lineIndex = 0;
    function printBootLine() {
      if (lineIndex < bootLines.length) {
        appendTerminalLine(bootLines[lineIndex], "boot-sequence");
        lineIndex++;
        setTimeout(printBootLine, 120);
      }
    }
    printBootLine();
  }

  function appendTerminalLine(text, className = "") {
    const line = document.createElement("div");
    line.className = `terminal-line ${className}`;
    line.textContent = text;
    terminalScreen.appendChild(line);
    terminalScreen.scrollTop = terminalScreen.scrollHeight;
  }

  // Typewriter outputs simulation (line by line in sequence)
  function typeTerminalOutput(htmlContent) {
    // Split by <br> or \n to get individual lines
    const lines = htmlContent.split(/<br>|\n/);
    let currentLineIndex = 0;

    // Helper to toggle interface controls to prevent concurrent input command overlap
    function setTerminalControlsDisabled(disabled) {
      terminalInput.disabled = disabled;
      terminalInput.placeholder = disabled ? "Neeraj-Bot typing response..." : "Type a command (e.g. /skills)...";
      
      presetBtns.forEach(btn => {
        btn.disabled = disabled;
        if (disabled) {
          btn.style.opacity = "0.5";
          btn.style.cursor = "not-allowed";
        } else {
          btn.style.opacity = "";
          btn.style.cursor = "";
        }
      });

      const submitBtn = terminalForm.querySelector(".terminal-submit-btn");
      if (submitBtn) submitBtn.disabled = disabled;
    }

    // Disable input interface controls
    setTerminalControlsDisabled(true);

    function typeNextLine() {
      if (currentLineIndex >= lines.length) {
        // Finished typing all lines, re-enable user inputs
        setTerminalControlsDisabled(false);
        terminalInput.focus();
        return;
      }

      const rawLineText = lines[currentLineIndex];
      const lineDiv = document.createElement("div");
      lineDiv.className = "terminal-line output-text";
      terminalScreen.appendChild(lineDiv);

      let charIndex = 0;
      
      function typeChar() {
        if (charIndex < rawLineText.length) {
          lineDiv.textContent += rawLineText.charAt(charIndex);
          charIndex++;
          terminalScreen.scrollTop = terminalScreen.scrollHeight;
          setTimeout(typeChar, 8); // Typing speed per character
        } else {
          // Finished typing current line, proceed to next line after a short delay
          currentLineIndex++;
          terminalScreen.scrollTop = terminalScreen.scrollHeight;
          setTimeout(typeNextLine, 60); // 60ms delay between lines for cool sequence effect
        }
      }

      typeChar();
    }

    typeNextLine();
  }


  // Terminal commands handling logic
  function processCommand(cmd) {
    const cleanCmd = cmd.trim().toLowerCase();
    
    if (cleanCmd === "") return;

    appendTerminalLine(`neeraj_bot@model:~# ${cmd}`, "user-entered");

    if (cleanCmd === "clear") {
      terminalScreen.innerHTML = `
        <div class="terminal-line">Terminal console cleared.</div>
        <div class="terminal-line">Type 'help' for available queries.</div>
      `;
      return;
    }

    if (cleanCmd === "help") {
      const helpMsg = `Available commands:<br>
      /profile  - Brief career summary and qualifications<br>
      /skills   - Breakdown of technical tool stacks<br>
      /projects - Summarized catalog of key achievements<br>
      /gate     - GATE 2026 certification status<br>
      /why-hire - Summary value pitch for ML roles<br>
      clear     - Clears the console window`;
      typeTerminalOutput(helpMsg);
      return;
    }

    switch (cleanCmd) {
      case "/profile":
        typeTerminalOutput(`Neeraj Kumar | Data Scientist & AI/ML Engineer
--------------------------------------------------
Education:
- B.S. in Data Science & Applications, IIT Madras (CGPA: 7.65)
- B.Tech in Information Technology, REC Bijnor (CGPA: 7.84, Top 10 Rank)
Achievements & Experience:
- Qualified GATE 2026 (Computer Science & Eng.)
- LeAP Next Gen Intern at Lenovo (Summer 2026)
- B.Tech Class Representative (2025-2027)
Seeking: AI/ML Engineering & Analytics Roles/Internships.`);
        break;

      case "/skills":
        typeTerminalOutput(`Technical Capability Map:
- Programming: Python, SQL, C
- Data Science: Pandas, NumPy, Matplotlib, Seaborn
- Machine Learning: Scikit-learn, NLP, Deep Learning, LangChain, RAG Systems
- Business Intelligence: Power BI, Excel dashboards
- Software & Dev: Flask (APIs), Git, GitHub, SQLite, Redis, Celery`);
        break;

      case "/projects":
        typeTerminalOutput(`Selected ML/Data Projects:
1. Kidney Disease Classification:
   Deep learning pipeline using CNNs (VGG16), MLflow, DVC, and Docker.
2. AMRIT Pharmacy Optimization:
   Analyzed 56K+ transactions using Python to optimize inventory metrics.
3. Comment Category Classification:
   Developed NLP prediction classifiers using Scikit-Learn.
4. IT & Business Cost Overview:
   Built interactive dashboards with Power BI and Excel.
5. Quiz Master Backend:
   Full-stack task queuing systems using Flask, Redis, and Celery.`);
        break;

      case "/gate":
        typeTerminalOutput(`GATE Certification:
--------------------------------------------------
Exam: GATE 2026 (Computer Science & Information Technology)
Status: Qualified (CSE)
Certificate: https://drive.google.com/file/d/1towJFGkqurTibie2kjY5d314Rw_ELIWb/view?usp=sharing
Competencies Verified: Algorithm Design, Data Structures, DBMS, Operating Systems, Computer Networks, Linear Algebra.`);
        break;

      case "/why-hire":
        typeTerminalOutput(`Neeraj Kumar Value Proposition:
1. Rigorous Data Foundations: Trained in statistical learning, algorithms, and models directly through IIT Madras.
2. CS Proficiency: Proven core computer science knowledge via GATE 2026 CSE qualification.
3. System Integration: Capable of building backend REST APIs (Flask) and background queues (Redis/Celery) to serve model inferences.
4. Professional Leadership: Proven leadership skills gained coordinating student councils and offline events at IIT Madras.`);
        break;

      default:
        appendTerminalLine(`Error: Command '${cmd}' not recognized. Type 'help' to see options.`, "error-text");
        break;
    }
  }

  // Handle Preset Clicks
  presetBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      // Verify console is unlocked
      if (neuralInterface.classList.contains("locked")) return;
      
      const cmd = btn.getAttribute("data-cmd");
      processCommand(cmd);
    });
  });

  // Handle Input Form submit
  terminalForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (neuralInterface.classList.contains("locked")) return;
    
    const cmd = terminalInput.value;
    if (cmd.trim() !== "") {
      processCommand(cmd);
      terminalInput.value = "";
    }
  });

  // ==========================================
  // CONTACT FORM INTERACTIVE RESPONSE
  // ==========================================

  if (contactForm) {
    contactForm.addEventListener("submit", (e) => {
      e.preventDefault();
      
      const name = document.getElementById("form-name").value;
      const email = document.getElementById("form-email").value;
      const subject = document.getElementById("form-subject").value;
      const message = document.getElementById("form-message").value;

      formFeedback.className = "form-feedback font-mono";
      formFeedback.textContent = "Transmitting message packet...";

      // Simulate network request
      setTimeout(() => {
        formFeedback.className = "form-feedback success font-mono";
        formFeedback.textContent = `Transmission Successful! Thank you, ${name}. Neeraj-Bot will respond shortly.`;
        contactForm.reset();
      }, 1500);
    });
  }
});
