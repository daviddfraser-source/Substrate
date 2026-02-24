export type PacketStatus = "pending" | "in_progress" | "done" | "failed" | "blocked";

export interface WbsPacketRow {
  id: string;
  parentId?: string;
  wbsRef: string;
  title: string;
  owner?: string;
  priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: PacketStatus;
  blockedByCount: number;
}

export interface RolePermissions {
  canView: boolean;
  canEdit: boolean;
  canBulkEdit: boolean;
}
