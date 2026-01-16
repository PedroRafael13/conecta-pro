'use client';

import { createContext, useContext, useState, type ReactNode } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/shared/utils/cn';

// Context
interface TabsContextValue {
  activeTab: string;
  setActiveTab: (value: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabsContext() {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tabs components must be used within a Tabs provider');
  }
  return context;
}

// Tabs Root
interface TabsProps {
  defaultValue: string;
  value?: string;
  onValueChange?: (value: string) => void;
  children: ReactNode;
  className?: string;
}

export function Tabs({
  defaultValue,
  value,
  onValueChange,
  children,
  className,
}: TabsProps) {
  const [internalValue, setInternalValue] = useState(defaultValue);

  const activeTab = value ?? internalValue;
  const setActiveTab = (newValue: string) => {
    setInternalValue(newValue);
    onValueChange?.(newValue);
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  );
}

// Tabs List
interface TabsListProps {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'pills' | 'underline';
}

export function TabsList({ children, className, variant = 'default' }: TabsListProps) {
  const variantClasses = {
    default: 'flex items-center gap-1 p-1 bg-bg-tertiary rounded-lg',
    pills: 'flex items-center gap-2',
    underline: 'flex items-center gap-4 border-b border-border-subtle',
  };

  return (
    <div className={cn(variantClasses[variant], className)} role="tablist">
      {children}
    </div>
  );
}

// Tab Trigger
interface TabsTriggerProps {
  value: string;
  children: ReactNode;
  className?: string;
  disabled?: boolean;
  icon?: ReactNode;
  badge?: ReactNode;
}

export function TabsTrigger({
  value,
  children,
  className,
  disabled,
  icon,
  badge,
}: TabsTriggerProps) {
  const { activeTab, setActiveTab } = useTabsContext();
  const isActive = activeTab === value;

  return (
    <button
      role="tab"
      aria-selected={isActive}
      aria-controls={`tabpanel-${value}`}
      disabled={disabled}
      onClick={() => setActiveTab(value)}
      className={cn(
        'relative px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        isActive
          ? 'text-text-primary'
          : 'text-text-secondary hover:text-text-primary',
        className
      )}
    >
      {isActive && (
        <motion.div
          layoutId="activeTab"
          className="absolute inset-0 bg-bg-secondary rounded-md shadow-sm"
          transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
        />
      )}
      <span className="relative flex items-center gap-2">
        {icon}
        {children}
        {badge}
      </span>
    </button>
  );
}

// Tab Content
interface TabsContentProps {
  value: string;
  children: ReactNode;
  className?: string;
}

export function TabsContent({ value, children, className }: TabsContentProps) {
  const { activeTab } = useTabsContext();

  if (activeTab !== value) return null;

  return (
    <motion.div
      role="tabpanel"
      id={`tabpanel-${value}`}
      aria-labelledby={`tab-${value}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className={cn('mt-4', className)}
    >
      {children}
    </motion.div>
  );
}

// Simple Tab Bar (alternative simpler implementation)
interface SimpleTab {
  value: string;
  label: string;
  icon?: ReactNode;
  badge?: ReactNode;
  disabled?: boolean;
}

interface SimpleTabBarProps {
  tabs: SimpleTab[];
  value: string;
  onChange: (value: string) => void;
  className?: string;
  variant?: 'default' | 'pills' | 'underline';
}

export function SimpleTabBar({
  tabs,
  value,
  onChange,
  className,
  variant = 'default',
}: SimpleTabBarProps) {
  const variantClasses = {
    default: {
      container: 'flex items-center gap-1 p-1 bg-bg-tertiary rounded-lg',
      tab: 'px-4 py-2 rounded-md text-sm font-medium',
      active: 'bg-bg-secondary text-text-primary shadow-sm',
      inactive: 'text-text-secondary hover:text-text-primary',
    },
    pills: {
      container: 'flex items-center gap-2',
      tab: 'px-4 py-2 rounded-full text-sm font-medium border',
      active: 'bg-accent-primary/10 text-accent-primary border-accent-primary/30',
      inactive: 'text-text-secondary border-transparent hover:bg-bg-tertiary',
    },
    underline: {
      container: 'flex items-center gap-4 border-b border-border-subtle',
      tab: 'px-1 py-3 text-sm font-medium border-b-2 -mb-px',
      active: 'text-accent-primary border-accent-primary',
      inactive: 'text-text-secondary border-transparent hover:text-text-primary',
    },
  };

  const styles = variantClasses[variant];

  return (
    <div className={cn(styles.container, className)} role="tablist">
      {tabs.map((tab) => (
        <button
          key={tab.value}
          role="tab"
          aria-selected={value === tab.value}
          disabled={tab.disabled}
          onClick={() => onChange(tab.value)}
          className={cn(
            styles.tab,
            'transition-all duration-200',
            'focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            value === tab.value ? styles.active : styles.inactive
          )}
        >
          <span className="flex items-center gap-2">
            {tab.icon}
            {tab.label}
            {tab.badge}
          </span>
        </button>
      ))}
    </div>
  );
}
