export type PermissionContext = {
  userId: string;
  role: "reader" | "editor" | "admin" | "support";
  orgId: string;
  featureFlags?: Record<string, boolean>;
};

export type Ability = {
  can: (action: string, resource: string) => boolean;
  cannot: (action: string, resource: string) => boolean;
};

export function defineAbilities(ctx: PermissionContext): Ability {
  const roleMap: Record<PermissionContext["role"], string[]> = {
    reader: ["read:article", "read:comment"],
    editor: ["read:article", "create:comment", "update:article"],
    admin: ["*"],
    support: ["read:article", "read:user"],
  };

  const allowed = roleMap[ctx.role] ?? [];

  return {
    can(action, resource) {
      if (ctx.role === "admin") {
        return true;
      }
      return allowed.some((perm) => perm === `${action}:${resource}` || perm === `${action}:*`);
    },
    cannot(action, resource) {
      return !this.can(action, resource);
    },
  };
}

export function assertCan(ctx: PermissionContext, action: string, resource: string) {
  const ability = defineAbilities(ctx);
  if (!ability.can(action, resource)) {
    console.warn("Policy denial", { ctx, action, resource });
    throw new Error("Unauthorized");
  }
  return true;
}
