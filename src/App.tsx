import { useCallback, useEffect, useRef, useState } from "react";
import OptionsScreen from "./components/OptionsScreen";
import PlaybackScreen from "./components/PlaybackScreen";
import type { VideoItem } from "./types";
import { clamp } from "./utils";

export default function App() {
  const [videos, setVideos] = useState<(VideoItem | null)[]>([]);
  const [rows, setRows] = useState(2);
  const [cols, setCols] = useState(2);
  const [speed, setSpeed] = useState(1.0);
  const [gap, setGap] = useState(0);
  const [gapColor, setGapColor] = useState("#000000");
  const [screen, setScreen] = useState<"options" | "playback">("options");
  const [guideVisible, setGuideVisible] = useState(false);

  // Live <video> elements in the playback grid (indexed by slot).
  const videoElsRef = useRef<(HTMLVideoElement | null)[]>([]);

  /* Replace the videos array; revoke object URLs that are no longer used. */
  const handleVideosChange = (next: (VideoItem | null)[]) => {
    const usedUrls = new Set(
      next.filter((v): v is VideoItem => !!v).map((v) => v.url)
    );
    for (const item of videos) {
      if (item && !usedUrls.has(item.url)) URL.revokeObjectURL(item.url);
    }
    setVideos(next);
  };

  const startPlayback = () => {
    setScreen("playback");
    document.documentElement.requestFullscreen?.();
  };

  const exitPlayback = useCallback(() => {
    videoElsRef.current.forEach((v) => {
      if (v) {
        v.pause();
        v.currentTime = 0;
        v.loop = false;
      }
    });
    setGuideVisible(false);
    setScreen("options");
    document.exitFullscreen?.();
  }, []);

  /* Register/unregister playback <video> elements; apply current speed on mount. */
  const registerVideo = useCallback(
    (index: number, el: HTMLVideoElement | null) => {
      if (el) el.playbackRate = speed;
      videoElsRef.current[index] = el;
    },
    [speed]
  );

  /* ===== KEYBOARD CONTROLS (playback screen only) ===== */
  useEffect(() => {
    if (screen !== "playback") return;

    const getVideos = () =>
      videoElsRef.current.filter((v): v is HTMLVideoElement => !!v);

    const playAll = () =>
      getVideos().forEach((v) => {
        v.loop = false;
        void v.play();
      });

    const pauseAll = () => getVideos().forEach((v) => v.pause());

    const togglePause = () => {
      const vids = getVideos();
      if (vids.length === 0) return;
      if (vids[0].paused) playAll();
      else pauseAll();
    };

    const stopAll = () =>
      getVideos().forEach((v) => {
        v.pause();
        v.currentTime = 0;
        v.loop = false;
      });

    const playAllWithLoop = () =>
      getVideos().forEach((v) => {
        v.loop = true;
        v.currentTime = 0;
        void v.play();
      });

    const setRate = (delta: number) => {
      const rate = clamp(speed + delta, 0.25, 4.0);
      setSpeed(rate);
      getVideos().forEach((v) => (v.playbackRate = rate));
    };

    const resetRate = () => {
      setSpeed(1.0);
      getVideos().forEach((v) => (v.playbackRate = 1.0));
    };

    const onKey = (e: KeyboardEvent) => {
      if (e.key === " ") {
        e.preventDefault();
        togglePause();
      } else if (e.key === "p" || e.key === "P") playAll();
      else if (e.key === "s" || e.key === "S") stopAll();
      else if (e.key === "Enter") {
        e.preventDefault();
        playAllWithLoop();
      } else if (e.key === "l" || e.key === "L") setRate(0.25);
      else if (e.key === "j" || e.key === "J") setRate(-0.25);
      else if (e.key === "k" || e.key === "K") resetRate();
      else if (e.key === "g" || e.key === "G") setGuideVisible((v) => !v);
      else if (e.key === "Escape") exitPlayback();
    };

    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [screen, speed, exitPlayback]);

  return screen === "options" ? (
    <OptionsScreen
      videos={videos}
      rows={rows}
      cols={cols}
      speed={speed}
      gap={gap}
      gapColor={gapColor}
      onVideosChange={handleVideosChange}
      onRowsChange={setRows}
      onColsChange={setCols}
      onSpeedChange={setSpeed}
      onGapChange={setGap}
      onGapColorChange={setGapColor}
      onClear={() => handleVideosChange([])}
      onStart={startPlayback}
    />
  ) : (
    <PlaybackScreen
      videos={videos}
      rows={rows}
      cols={cols}
      gap={gap}
      gapColor={gapColor}
      guideVisible={guideVisible}
      registerVideo={registerVideo}
    />
  );
}
