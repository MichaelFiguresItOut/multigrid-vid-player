import { useRef, useState } from "react";
import KeyGuide from "./KeyGuide";
import type { VideoItem } from "../types";
import { clamp } from "../utils";

interface OptionsScreenProps {
  videos: (VideoItem | null)[];
  rows: number;
  cols: number;
  speed: number;
  gap: number;
  gapColor: string;
  onVideosChange: (videos: (VideoItem | null)[]) => void;
  onRowsChange: (rows: number) => void;
  onColsChange: (cols: number) => void;
  onSpeedChange: (speed: number) => void;
  onGapChange: (gap: number) => void;
  onGapColorChange: (color: string) => void;
  onClear: () => void;
  onStart: () => void;
}

export default function OptionsScreen({
  videos,
  rows,
  cols,
  speed,
  gap,
  gapColor,
  onVideosChange,
  onRowsChange,
  onColsChange,
  onSpeedChange,
  onGapChange,
  onGapColorChange,
  onClear,
  onStart,
}: OptionsScreenProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedCell, setSelectedCell] = useState<number | null>(null);
  const [dragOverCell, setDragOverCell] = useState<number | null>(null);

  const slots = rows * cols;

  /* ===== ADD VIDEOS (mirrors claudegridv14.py assignment logic) ===== */
  const handleFilesAdded = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    e.target.value = "";
    if (files.length === 0) return;

    const newVideos: VideoItem[] = files.map((file) => ({
      url: URL.createObjectURL(file),
      name: file.name,
    }));

    const next = [...videos];
    if (selectedCell !== null) {
      // Pad so assigning to a far cell leaves the same holes as in v14.
      while (next.length <= selectedCell) next.push(null);
    }

    if (selectedCell !== null && newVideos.length > 0) {
      // A cell is selected: assign the first new video to it,
      // then fill remaining videos into the next available slots.
      next[selectedCell] = newVideos[0];
      setSelectedCell(null);
      for (let i = 1; i < newVideos.length; i++) {
        const idx = next.findIndex((v) => !v);
        if (idx !== -1) next[idx] = newVideos[i];
        else next.push(newVideos[i]);
      }
    } else {
      // No cell selected: add videos to the next available slots.
      for (const video of newVideos) {
        const idx = next.findIndex((v) => !v);
        if (idx !== -1) next[idx] = video;
        else next.push(video);
      }
    }

    onVideosChange(next);
  };

  /* ===== DRAG & DROP SWAP BETWEEN CELLS ===== */
  const swapCells = (from: number, to: number) => {
    if (from === to || from < 0 || to < 0) return;
    const next = [...videos];
    [next[from], next[to]] = [next[to], next[from]];
    onVideosChange(next);
  };

  /* Click a cell: select it for assignment, then open the file picker. */
  const handleCellClick = (i: number) => {
    setSelectedCell(i);
    fileInputRef.current?.click();
  };

  return (
    <div id="optionsScreen">
      <div id="leftPanel">
        <h2>Multi Video Grid Player — Setup</h2>

        <div className="controls">
          <button onClick={() => fileInputRef.current?.click()}>Add Videos</button>
          <input
            ref={fileInputRef}
            type="file"
            accept="video/mp4"
            multiple
            hidden
            onChange={handleFilesAdded}
          />

          <label>
            Rows:{" "}
            <input
              type="number"
              min={1}
              max={5}
              value={rows}
              onChange={(e) => onRowsChange(clamp(+e.currentTarget.value || 1, 1, 5))}
            />
          </label>
          <label>
            Cols:{" "}
            <input
              type="number"
              min={1}
              max={5}
              value={cols}
              onChange={(e) => onColsChange(clamp(+e.currentTarget.value || 1, 1, 5))}
            />
          </label>

          <label>
            Speed:{" "}
            <input
              type="number"
              min={0.25}
              max={4}
              step={0.25}
              value={speed}
              style={{ width: 70 }}
              onChange={(e) => onSpeedChange(clamp(+e.currentTarget.value || 1, 0.25, 4))}
            />x
          </label>

          <label>
            Grid Line Thickness:{" "}
            <input
              type="number"
              min={0}
              max={20}
              value={gap}
              style={{ width: 60 }}
              onChange={(e) => onGapChange(clamp(+e.currentTarget.value || 0, 0, 20))}
            />px
          </label>
          <label>
            Grid Line Color:{" "}
            <input
              type="color"
              value={gapColor}
              onChange={(e) => onGapColorChange(e.currentTarget.value)}
            />
          </label>

          <button
            onClick={() => {
              setSelectedCell(null);
              setDragOverCell(null);
              onClear();
            }}
          >
            Clear All
          </button>
          <button onClick={onStart}>Start Playback</button>
        </div>

        {/* ===== PREVIEW GRID (OPTIONS SCREEN) ===== */}
        <div
          id="gridPreview"
          style={{
            gridTemplateColumns: `repeat(${cols}, 1fr)`,
            gridTemplateRows: `repeat(${rows}, 1fr)`,
          }}
        >
          {Array.from({ length: slots }, (_, i) => (
            <div
              key={i}
              className={`cell${selectedCell === i ? " selected" : ""}${
                dragOverCell === i ? " dragover" : ""
              }`}
              draggable
              onClick={() => handleCellClick(i)}
              onDragStart={(e) => e.dataTransfer.setData("text/plain", String(i))}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOverCell(i);
              }}
              onDragLeave={() => setDragOverCell(null)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOverCell(null);
                const from = +e.dataTransfer.getData("text/plain");
                swapCells(from, i);
              }}
            >
              {videos[i] ? videos[i].name : "(empty)"}
            </div>
          ))}
        </div>
      </div>

      <KeyGuide />
    </div>
  );
}
