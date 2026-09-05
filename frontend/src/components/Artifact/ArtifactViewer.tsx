"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { SandboxedIframe } from "./SandboxedIframe";

export type Artifact = { artifact_type: "markdown" | "html"; title: string; content: string };

export function ArtifactViewer({ artifact }: { artifact: Artifact | null }) {
  if (!artifact) {
    return (
      <div className="empty-artifact">
        <div className="artifact-icon">✦</div>
        <h2>Artifact workspace</h2>
        <p>Ask the assistant to turn the current discussion into a Markdown document or interactive HTML artifact.</p>
      </div>
    );
  }

  return (
    <div className="artifact-shell">
      <div className="artifact-header">
        <div>
          <span className="eyebrow">Artifact</span>
          <h2>{artifact.title}</h2>
        </div>
        <span className="status-pill">Sandboxed preview</span>
      </div>
      <div className="artifact-content">
        {artifact.artifact_type === "markdown" ? (
          <article className="markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.content}</ReactMarkdown>
          </article>
        ) : (
          <SandboxedIframe content={artifact.content} title={artifact.title} />
        )}
      </div>
    </div>
  );
}
