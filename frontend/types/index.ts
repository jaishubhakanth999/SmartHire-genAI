export type Experience = {
  title: string;
  company: string;
  start_date?: string | null;
  end_date?: string | null;
  description?: string | null;
};

export type Education = {
  degree: string;
  institution: string;
  year?: string | null;
};

export type ParsedResume = {
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  target_role?: string | null;
  skills: string[];
  experience: Experience[];
  education: Education[];
};

export type ResumeRecord = {
  id: string;
  filename: string;
  parsed: ParsedResume;
  created_at: string;
};

export type JobMatch = {
  id: string;
  title: string;
  company: string | null;
  skills: string | null;
  description: string;
  similarity: number;
};

export type ChatMessage = {
  id?: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  grounded?: boolean;
  blocked?: boolean;
};

export type Profile = {
  id: string;
  email: string;
  full_name?: string | null;
  role: "user" | "admin";
};
