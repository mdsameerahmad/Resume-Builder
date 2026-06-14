# ATS Resume Agent Frontend

This is the frontend client for the ATS Resume Agent, built with **Next.js 15 (App Router)**, **React 19**, **Tailwind CSS v4**, and **Zustand** for state management. 

It provides a clean, responsive, and intuitive user interface to guide users through uploading their resumes, analyzing job descriptions, reviewing gap analyses, and downloading an ATS-optimized, layout-preserved PDF.

## 🚀 Tech Stack

- **Framework**: [Next.js 15](https://nextjs.org/) (App Router)
- **Library**: [React 19](https://react.dev/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **State Management**: [Zustand](https://github.com/pmndrs/zustand) (with `persist` middleware for local storage)
- **HTTP Client**: [Axios](https://axios-http.com/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Utilities**: `clsx` and `tailwind-merge` for dynamic class names

---

## 🏗️ Architecture & Directory Structure

```text
ats-resume-agent/
├── app/                  # Next.js App Router (Pages and Layouts)
│   ├── globals.css       # Global styles and Tailwind imports
│   ├── layout.tsx        # Root layout with hydration suppression
│   ├── page.tsx          # Landing/Dashboard page
│   ├── upload/           # Step 1: Resume Upload
│   ├── jobs/             # Step 2: JD Input
│   ├── analysis/         # Step 3: Gap Analysis & Optimization Trigger
│   ├── optimize/         # Step 4: Processing State
│   └── pdf/              # Step 5: PDF Download & Preview
├── components/           # Reusable UI Components
│   ├── navbar/           # Global Navigation
│   ├── resume/           # ResumeUploader and preview components
│   └── jobs/             # JDInput components
├── lib/                  # Utilities, API, and State
│   ├── api.ts            # Axios client and API route definitions
│   ├── store.ts          # Zustand store for cross-step state persistence
│   ├── types.ts          # TypeScript interfaces for API payloads
│   └── utils.ts          # Helper functions (e.g., cn for tailwind)
└── public/               # Static assets
```

---

## 🔄 User Workflow

The application follows a strict step-by-step workflow:

1. **Upload (`/upload`)**: Users upload an existing PDF resume. The frontend calls the backend to upload, extract text/layout, parse it into a Master Profile via AI, and generate a layout-preserving template.
2. **Job Description (`/jobs`)**: Users paste the target Job Description (JD). The backend analyzes it to extract ATS keywords, skills, and requirements.
3. **Gap Analysis (`/analysis`)**: The frontend requests a comparison between the Master Profile and the JD. It displays a visual breakdown of missing skills, matched keywords, and overall ATS scores.
4. **Optimization (`/optimize`)**: A loading screen that triggers the AI to rewrite and target the resume content specifically for the JD.
5. **PDF Generation (`/pdf`)**: Triggers the backend Playwright engine to render the optimized JSON into the generated layout template, compressing it to 1 page, and returning a downloadable PDF link.

---

## 🔌 API Integration (FastAPI Backend)

The frontend communicates with the backend via Axios in `lib/api.ts`. It strictly maps to the backend's `/api/v1` routers:

- **Resume Upload & Parsing**: 
  - `POST /api/v1/resume/upload` (Multipart Form)
  - `POST /api/v1/resume/extract/{id}`
  - `POST /api/v1/resume/parse/{id}`
  - `POST /api/v1/template/generate/{id}`
- **Job Description**: 
  - `POST /api/v1/jd/analyze` (JSON payload: `job_description`)
- **Intelligence**: 
  - `POST /api/v1/gap/analyze`
  - `POST /api/v1/optimizer/generate`
- **Rendering**: 
  - `POST /api/v1/pdf/generate`

**Note**: State (like `resumeId`, `jobId`, `optimizedId`, `generatedId`) is preserved in `localStorage` via Zustand, ensuring users do not lose their progress if they refresh the page.

---

## 🛠️ Getting Started

### 1. Prerequisites

Make sure you have [Node.js](https://nodejs.org/) (v20+) installed.

### 2. Installation

```bash
cd ats-resume-agent
npm install
# or
yarn install
```

### 3. Environment Variables

Create a `.env.local` file in the root of `ats-resume-agent`:

```env
# URL of your running FastAPI backend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Running the Development Server

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### 5. Common Issues & Troubleshooting

- **Hydration Mismatches**: If you see hydration warnings in the console, it is typically caused by browser extensions injecting attributes into the DOM (like `data-new-gr-c-s-check-loaded`). The `<html>` and `<body>` tags in `app/layout.tsx` use `suppressHydrationWarning` to mitigate this.
- **API CORS Errors**: Ensure the backend FastAPI server has `http://localhost:3000` added to its `BACKEND_CORS_ORIGINS` setting.
- **Styles Not Loading**: Ensure `globals.css` is imported in `app/layout.tsx`. Tailwind v4 uses the `@tailwindcss/postcss` plugin, requiring standard CSS imports.
