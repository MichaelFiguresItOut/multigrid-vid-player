import { Fragment } from "react";

const KEYS: Array<[string, string]> = [
  ["Space", "Pause/Unpause"],
  ["P", "Play all"],
  ["S", "Stop all"],
  ["Enter", "Play all (looping)"],
  ["L", "Speed +0.25x"],
  ["J", "Speed -0.25x"],
  ["K", "Reset speed to 1x"],
  ["G", "Toggle this guide"],
  ["Esc", "Exit playback"],
];

interface KeyGuideProps {
  floating?: boolean;
}

export default function KeyGuide({ floating = false }: KeyGuideProps) {
  return (
    <div id={floating ? "playbackKeyGuide" : "keyGuide"}>
      <h3>Keyboard Controls</h3>
      <div className="guide-grid">
        {KEYS.map(([key, description]) => (
          <Fragment key={key}>
            <strong>{key}</strong>
            <span>{description}</span>
          </Fragment>
        ))}
      </div>
    </div>
  );
}
