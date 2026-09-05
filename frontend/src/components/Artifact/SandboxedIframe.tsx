"use client";

import DOMPurify from "dompurify";
import { useMemo } from "react";

export function SandboxedIframe({ content, title }: { content: string; title: string }) {
  const cleanHtml = useMemo(
    () =>
      DOMPurify.sanitize(content, {
        WHOLE_DOCUMENT: true,
        ADD_TAGS: ["style", "link", "script"],
        ADD_ATTR: ["target"],
      }),
    [content],
  );

  return (
    <iframe
      title={title}
      srcDoc={cleanHtml}
      sandbox="allow-scripts"
      className="artifact-frame"
    />
  );
}
