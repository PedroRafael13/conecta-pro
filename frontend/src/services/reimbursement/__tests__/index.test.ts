import { describe, it, expect } from 'vitest';
import {
  reimbursementRequestService,
  reimbursementItemService,
  reimbursementAttachmentService,
  reimbursementApprovalService,
  reimbursementPaymentService,
} from '../index';

describe('services/reimbursement/index re-exports', () => {
  it('should re-export all services', () => {
    expect(reimbursementRequestService).toBeDefined();
    expect(reimbursementItemService).toBeDefined();
    expect(reimbursementAttachmentService).toBeDefined();
    expect(reimbursementApprovalService).toBeDefined();
    expect(reimbursementPaymentService).toBeDefined();
  });

  it('should have correct service methods', () => {
    expect(typeof reimbursementRequestService.list).toBe('function');
    expect(typeof reimbursementItemService.create).toBe('function');
    expect(typeof reimbursementAttachmentService.upload).toBe('function');
    expect(typeof reimbursementApprovalService.approve).toBe('function');
    expect(typeof reimbursementPaymentService.process).toBe('function');
  });
});
