// Design System Components - Conecta PRO
// Dark Mode Premium Theme

// Core Components
export { Button, buttonVariants, type ButtonProps } from './Button';
export { Card, CardHeader, CardBody, CardFooter, cardVariants, type CardProps, type CardHeaderProps } from './Card';
export { Input, inputVariants, type InputProps } from './Input';
export { Textarea, textareaVariants, type TextareaProps } from './Textarea';
export { Badge, badgeVariants, type BadgeProps } from './Badge';
export { Select, type SelectProps, type SelectOption } from './Select';

// Feedback Components
export { Modal, type ModalProps } from './Modal';
export { ToastProvider, useToast, type Toast, type ToastType } from './Toast';
export { Spinner, PageLoader, InlineLoader, ButtonLoader } from './Spinner';
export {
  Skeleton,
  SkeletonText,
  SkeletonCard,
  SkeletonTable,
  SkeletonStats
} from './Skeleton';
export { Tooltip, type TooltipProps } from './Tooltip';
export { Progress, CircularProgress, type ProgressProps, type CircularProgressProps } from './Progress';
export { EmptyState, type EmptyStateProps } from './EmptyState';

// Data Display
export { Avatar, AvatarGroup, avatarVariants, type AvatarProps, type AvatarGroupProps } from './Avatar';
export { StatCard, MiniStatCard, StatGrid, type StatCardProps, type MiniStatCardProps, type StatGridProps } from './StatCard';
export {
  Table,
  TableContainer,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  TableEmpty,
  DataTable,
  type Column,
  type DataTableProps,
  type TableRowProps,
  type TableHeadProps,
} from './Table';

// Navigation
export { Tabs, TabsList, TabsTrigger, TabsContent, SimpleTabBar } from './Tabs';
export { TabsTrigger as Tab } from './Tabs'; // Alias for compatibility
export { Dropdown, DropdownButton, type DropdownProps, type DropdownItem, type DropdownButtonProps } from './Dropdown';
