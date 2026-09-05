# Design Specification

## Design principles
1. **Research first:** the answer and its sources are the primary workspace.
2. **Artifacts are first-class:** generated documents and HTML are previewed beside the conversation.
3. **State is visible:** model, mode, retrieval status, and source count are explicit.
4. **Progressive disclosure:** detailed source metadata is available without overwhelming the chat.
5. **Fast scanning:** restrained typography, short labels, clear hierarchy, and compact source cards.

## Information architecture
- **Header:** product identity + New chat.
- **Control strip:** provider, mode, and live request status.
- **Conversation:** user/assistant turns.
- **Composer:** prompt input and send state.
- **Artifact workspace:** Markdown/HTML preview.
- **Sources panel:** latest retrieved transcript chunks and similarity scores.

## Interaction states
- **Empty:** example questions guide the user.
- **Retrieving:** status changes to “Retrieving transcripts…”.
- **Generating:** status identifies the selected provider.
- **Success:** response remains visible and sources populate the side panel.
- **No grounding:** required insufficient-information message is returned.
- **Service failure:** error is displayed in the response area and status strip.
- **Artifact:** preview replaces the empty artifact state immediately after the artifact event arrives.

## Responsive behavior
At desktop widths the product uses a two-pane research workspace. Below 900px the layout collapses into a single vertical flow, preserving the chat first and artifact/source workspace below it.

## Accessibility
- Native form controls and buttons.
- Labels associated with provider/mode selectors.
- High-contrast text and borders.
- No interaction relies solely on color.
- Keyboard-friendly composer: Enter submits, Shift+Enter inserts a newline.
- Artifact iframe has a descriptive title.

## Artifact security UX
The viewer labels previews as “Sandboxed preview” so evaluators understand that generated HTML is intentionally isolated. The application does not present artifact HTML as trusted application markup.
