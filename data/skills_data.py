# data/skills_data.py
# Comprehensive skill dictionaries for extraction and matching

SKILLS_DB = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#", "go", "golang",
        "rust", "kotlin", "swift", "r", "scala", "ruby", "php", "perl", "bash", "shell",
        "powershell", "matlab", "julia", "dart", "lua", "haskell", "elixir", "clojure",
        "groovy", "fortran", "cobol", "assembly", "vba", "objective-c", "f#"
    ],
    "Frontend": [
        "html", "css", "react", "reactjs", "react.js", "angular", "angularjs", "vue",
        "vuejs", "vue.js", "svelte", "next.js", "nextjs", "nuxt", "gatsby", "bootstrap",
        "tailwind", "tailwindcss", "sass", "scss", "less", "jquery", "webpack", "vite",
        "babel", "redux", "mobx", "zustand", "graphql", "apollo", "storybook", "figma",
        "webgl", "three.js", "d3.js", "chartjs", "material-ui", "mui", "ant design",
        "chakra ui", "styled-components", "emotion", "framer motion"
    ],
    "Backend": [
        "node.js", "nodejs", "express", "expressjs", "django", "flask", "fastapi",
        "spring", "spring boot", "asp.net", "laravel", "rails", "ruby on rails",
        "gin", "fiber", "actix", "nest.js", "nestjs", "graphql", "rest", "restful",
        "grpc", "websocket", "microservices", "kafka", "rabbitmq", "celery", "redis",
        "nginx", "apache", "gunicorn", "uvicorn", "sqlalchemy", "hibernate", "prisma",
        "sequelize", "mongoose", "typeorm"
    ],
    "Databases": [
        "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis", "cassandra",
        "dynamodb", "elasticsearch", "neo4j", "oracle", "mssql", "sql server",
        "mariadb", "cockroachdb", "firebase", "supabase", "planetscale", "snowflake",
        "bigquery", "redshift", "hive", "spark sql", "influxdb", "timescaledb",
        "couchdb", "arangodb", "rethinkdb", "memcached"
    ],
    "Cloud": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp",
        "google cloud", "google cloud platform", "heroku", "digitalocean", "vercel",
        "netlify", "cloudflare", "ec2", "s3", "lambda", "rds", "ecs", "eks",
        "cloud functions", "cloud run", "gke", "aks", "terraform", "ansible",
        "cloudformation", "pulumi", "kubernetes", "k8s", "docker", "helm",
        "istio", "prometheus", "grafana", "datadog", "new relic"
    ],
    "AI/ML": [
        "machine learning", "deep learning", "artificial intelligence", "neural network",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "xgboost",
        "lightgbm", "catboost", "pandas", "numpy", "matplotlib", "seaborn", "plotly",
        "opencv", "nlp", "natural language processing", "computer vision", "cv",
        "transformers", "hugging face", "bert", "gpt", "llm", "large language model",
        "reinforcement learning", "generative ai", "stable diffusion", "langchain",
        "openai", "anthropic", "llama", "mistral", "spacy", "nltk", "gensim",
        "fastai", "mlflow", "kubeflow", "airflow", "feature engineering",
        "model deployment", "mlops", "data science", "statistics", "probability"
    ],
    "Tools & Platforms": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello",
        "slack", "docker", "kubernetes", "jenkins", "ci/cd", "github actions",
        "gitlab ci", "circleci", "travis ci", "sonarqube", "postman", "swagger",
        "openapi", "linux", "ubuntu", "centos", "macos", "windows", "bash",
        "vim", "vscode", "intellij", "eclipse", "xcode", "android studio",
        "figma", "adobe xd", "sketch", "invision", "zeplin", "notion",
        "airtable", "monday.com", "asana", "datadog", "splunk", "elk stack",
        "vagrant", "packer", "makefile", "npm", "yarn", "pip", "conda",
        "virtualenv", "poetry", "maven", "gradle"
    ]
}

# Action verbs that strengthen resumes
ACTION_VERBS = {
    "strong": [
        "architected", "spearheaded", "orchestrated", "pioneered", "revolutionized",
        "transformed", "optimized", "engineered", "designed", "developed", "built",
        "implemented", "deployed", "automated", "streamlined", "accelerated",
        "increased", "decreased", "reduced", "improved", "enhanced", "launched",
        "delivered", "led", "managed", "directed", "mentored", "collaborated",
        "integrated", "migrated", "refactored", "scaled", "secured", "monitored",
        "analyzed", "researched", "created", "established", "maintained"
    ],
    "weak": [
        "worked", "helped", "assisted", "did", "made", "used", "tried", "attempted",
        "participated", "involved", "contributed", "supported", "handled", "dealt"
    ]
}

# Soft skills keywords
SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem-solving", "critical thinking",
    "time management", "adaptability", "creativity", "collaboration", "attention to detail",
    "project management", "analytical", "interpersonal", "presentation", "negotiation",
    "decision making", "conflict resolution", "mentoring", "coaching", "strategic thinking",
    "multitasking", "organization", "self-motivated", "proactive", "detail-oriented"
]

# Job role required skills mapping
JOB_ROLES = {
    "Frontend Developer": {
        "required": ["html", "css", "javascript", "react", "responsive design"],
        "preferred": ["typescript", "vue", "angular", "webpack", "tailwind", "redux", "graphql", "testing"],
        "bonus": ["next.js", "svelte", "webgl", "animation", "accessibility", "performance optimization"],
        "description": "Builds user interfaces and interactive web experiences"
    },
    "Backend Developer": {
        "required": ["python", "java", "node.js", "sql", "rest api", "databases"],
        "preferred": ["docker", "microservices", "redis", "message queues", "authentication", "testing"],
        "bonus": ["kubernetes", "grpc", "elasticsearch", "caching", "performance tuning"],
        "description": "Develops server-side logic, APIs, and database integrations"
    },
    "Full Stack Developer": {
        "required": ["javascript", "html", "css", "react", "node.js", "sql", "rest api"],
        "preferred": ["typescript", "docker", "mongodb", "redis", "ci/cd", "cloud"],
        "bonus": ["kubernetes", "microservices", "graphql", "testing", "devops"],
        "description": "Works across the entire technology stack from UI to databases"
    },
    "Data Analyst": {
        "required": ["python", "sql", "excel", "data visualization", "statistics"],
        "preferred": ["pandas", "numpy", "tableau", "power bi", "matplotlib", "r"],
        "bonus": ["machine learning", "spark", "airflow", "dbt", "snowflake", "bigquery"],
        "description": "Analyzes data to extract insights and support business decisions"
    },
    "ML Engineer": {
        "required": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn"],
        "preferred": ["mlops", "docker", "kubernetes", "airflow", "mlflow", "sql", "cloud"],
        "bonus": ["transformers", "distributed training", "model optimization", "onnx", "triton"],
        "description": "Builds and deploys production machine learning systems"
    },
    "Python Developer": {
        "required": ["python", "django", "flask", "fastapi", "sql", "rest api"],
        "preferred": ["docker", "celery", "redis", "pytest", "git", "linux"],
        "bonus": ["kubernetes", "aws", "microservices", "graphql", "async programming"],
        "description": "Develops applications and services using Python ecosystem"
    },
    "DevOps Engineer": {
        "required": ["docker", "kubernetes", "ci/cd", "linux", "bash", "cloud", "git"],
        "preferred": ["terraform", "ansible", "jenkins", "prometheus", "grafana", "nginx"],
        "bonus": ["service mesh", "gitops", "security", "cost optimization", "chaos engineering"],
        "description": "Manages infrastructure, deployment pipelines, and operational reliability"
    },
    "Data Scientist": {
        "required": ["python", "machine learning", "statistics", "sql", "data analysis", "scikit-learn"],
        "preferred": ["tensorflow", "pytorch", "spark", "r", "tableau", "experimentation"],
        "bonus": ["nlp", "computer vision", "causal inference", "bayesian methods", "deep learning"],
        "description": "Applies statistical and ML methods to solve complex business problems"
    }
}

# Resume section keywords for detection
SECTION_KEYWORDS = {
    "experience": ["experience", "work experience", "employment", "work history", "professional experience",
                   "career history", "positions held", "job history", "internship", "internships"],
    "education": ["education", "academic", "qualification", "degree", "university", "college",
                  "school", "courses", "certification", "certifications", "training"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "expertise",
               "proficiencies", "competencies", "tools", "languages", "frameworks"],
    "projects": ["projects", "personal projects", "academic projects", "side projects",
                 "portfolio", "open source", "github projects", "key projects"],
    "summary": ["summary", "objective", "profile", "about", "overview", "professional summary",
                "career objective", "personal statement"],
    "achievements": ["achievements", "accomplishments", "awards", "honors", "recognition",
                     "publications", "patents", "volunteer"],
    "contact": ["email", "phone", "linkedin", "github", "portfolio", "website", "address", "mobile"]
}

# Common resume keywords that ATS systems look for
ATS_KEYWORDS = [
    "results-driven", "proven track record", "strong analytical", "excellent communication",
    "team player", "fast learner", "problem solver", "detail-oriented", "self-motivated",
    "cross-functional", "stakeholder", "agile", "scrum", "kanban", "sprint",
    "roi", "kpi", "metrics", "data-driven", "scalable", "robust", "production",
    "enterprise", "b2b", "b2c", "saas", "api", "sdk", "mvp", "poc"
]
