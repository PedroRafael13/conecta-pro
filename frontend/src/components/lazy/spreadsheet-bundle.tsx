/**
 * Spreadsheet Bundle - Carregado sob demanda
 */
'use client';

import { useState } from 'react';

interface SpreadsheetBundleProps {
  data: any[][];
  onChange?: (data: any[][]) => void;
  readOnly?: boolean;
}

export default function SpreadsheetBundle({ data, onChange, readOnly }: SpreadsheetBundleProps) {
  const [localData, setLocalData] = useState(data);

  const handleCellChange = (row: number, col: number, value: string) => {
    if (readOnly) return;

    const newData = [...localData];
    if (!newData[row]) newData[row] = [];
    newData[row][col] = value;

    setLocalData(newData);
    onChange?.(newData);
  };

  return (
    <div className="overflow-auto border rounded-lg">
      <table className="w-full text-sm">
        <tbody>
          {localData.map((row, rowIndex) => (
            <tr key={rowIndex} className="border-b">
              {row.map((cell, colIndex) => (
                <td key={colIndex} className="border-r p-2 min-w-[100px]">
                  <input
                    type="text"
                    value={cell || ''}
                    onChange={(e) => handleCellChange(rowIndex, colIndex, e.target.value)}
                    disabled={readOnly}
                    className="w-full bg-transparent outline-none"
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
