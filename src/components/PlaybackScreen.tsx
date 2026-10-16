import KeyGuide from "./KeyGuide";
import type { VideoItem } from "../types";

interface PlaybackScreenProps {
  videos: (VideoItem | null)[];
  rows: number;
  cols: number;
  gap: number;
  gapColor: string;
  guideVisible: boolean;
  registerVideo: (index: number, el: HTMLVideoElement | null) => void;
}

export default function PlaybackScreen({
  videos,
  rows,
  cols,
  gap,
  gapColor,
  guideVisible,
  registerVideo,
}: PlaybackScreenProps) {
  const slots = rows * cols;

  return (
    <div id="playbackScreen">
      {/* GRID DIVIDES THE ENTIRE SCREEN */}
      <div
        id="videoGrid"
        style={{
          gridTemplateColumns: `repeat(${cols}, 1fr)`,
          gridTemplateRows: `repeat(${rows}, 1fr)`,
          gap: `${gap}px`,
          background: gapColor,
        }}
      >
        {Array.from({ length: slots }, (_, i) => {
          const item = videos[i];
          if (!item) return null;
          return (
            <video
              key={item.url}
              ref={(el) => registerVideo(i, el)}
              src={item.url}
              preload="auto"
              playsInline
            />
          );
        })}
      </div>

      {guideVisible && <KeyGuide floating />}
    </div>
  );
}
