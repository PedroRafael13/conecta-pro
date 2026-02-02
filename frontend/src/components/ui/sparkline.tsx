'use client';

import dynamic from 'next/dynamic';
import { ComponentType } from 'react';

interface SparklineProps {
  data: number[];
  color?: string;
  height?: number;
}

// Wrapper com lazy load
const SparklineWrapper = dynamic(
  () => import('recharts').then((mod) => {
    const { LineChart, Line, ResponsiveContainer } = mod;

    return {
      default: ({ data, color = '#3b82f6', height = 40 }: SparklineProps) => {
        const chartData = data.map((value, index) => ({
          index,
          value,
        }));

        return (
          <ResponsiveContainer width="100%" height={height}>
            <LineChart data={chartData}>
              <Line
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        );
      }
    };
  }),
  { ssr: false }
) as ComponentType<SparklineProps>;

export function Sparkline(props: SparklineProps) {
  return <SparklineWrapper {...props} />;
}
