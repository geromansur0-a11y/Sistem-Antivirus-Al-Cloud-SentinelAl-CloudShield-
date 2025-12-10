import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

export default function FileDropZone({ onScan }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onScan(acceptedFiles[0]);
    }
  }, [onScan]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50 MB
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition
        ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300"}`}
    >
      <input {...getInputProps()} />
      <div className="text-4xl mb-3">📤</div>
      {isDragActive ? (
        <p>Lepaskan file di sini...</p>
      ) : (
        <p>
          Tarik file ke sini, atau <span className="text-blue-600 font-bold">klik untuk pilih</span>
        </p>
      )}
      <p className="text-sm text-gray-500 mt-2">Maks. 50 MB (PDF, DOCX, JS, EXE, ZIP, dll)</p>
    </div>
  );
      }
