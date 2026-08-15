import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi, AdminUserCreatePayload } from '../../api/users';
import { User, UserRole, UserStatus } from '../../types';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { Input, Select } from '../../components/ui/Input';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { formatDate } from '../../utils/formatters';
import {
  Users,
  Plus,
  AlertCircle,
} from 'lucide-react';

export const AdminUserManagement: React.FC = () => {
  const queryClient = useQueryClient();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<UserRole>('STUDENT');
  const [formError, setFormError] = useState<string | null>(null);

  const { data: users = [], isLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => usersApi.listUsersAdmin(0, 100),
  });

  const statusMutation = useMutation({
    mutationFn: ({ userId, status }: { userId: string; status: UserStatus }) =>
      usersApi.updateUserStatusAdmin(userId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
  });

  const createMutation = useMutation({
    mutationFn: (payload: AdminUserCreatePayload) => usersApi.createUserAdmin(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setIsAddModalOpen(false);
      setEmail('');
      setPassword('');
      setFullName('');
      setFormError(null);
    },
    onError: (err: any) => {
      setFormError(err.message || 'Failed to create user account.');
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || !fullName) {
      setFormError('All fields are required.');
      return;
    }

    setFormError(null);
    createMutation.mutate({
      email,
      password,
      full_name: fullName,
      role,
    });
  };

  const toggleStatus = (user: User) => {
    const newStatus: UserStatus = user.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE';
    statusMutation.mutate({ userId: user.id, status: newStatus });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">User Management</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Manage system access, account activations, and administrative roles.
          </p>
        </div>

        <Button
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => {
            setIsAddModalOpen(true);
            setFormError(null);
          }}
        >
          Create User
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-5 space-y-3">
              <CardSkeleton />
              <CardSkeleton />
            </div>
          ) : users.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<Users className="w-8 h-8 text-slate-400" />}
                title="No Users Registered"
                description="No users currently exist in the system database."
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="p-4">Name & Email</th>
                    <th className="p-4">Role</th>
                    <th className="p-4">Status</th>
                    <th className="p-4">Created Date</th>
                    <th className="p-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50/70 transition">
                      <td className="p-4">
                        <div className="font-bold text-slate-900">{u.full_name}</div>
                        <div className="font-mono text-[11px] text-slate-500">{u.email}</div>
                      </td>

                      <td className="p-4">
                        <Badge size="sm" status={u.role} />
                      </td>

                      <td className="p-4">
                        <Badge size="sm" status={u.status} />
                      </td>

                      <td className="p-4 text-slate-500">{formatDate(u.created_at.split('T')[0])}</td>

                      <td className="p-4 text-right">
                        <Button
                          size="sm"
                          variant={u.status === 'ACTIVE' ? 'outline' : 'success'}
                          onClick={() => toggleStatus(u)}
                          isLoading={statusMutation.isPending}
                        >
                          {u.status === 'ACTIVE' ? 'Suspend' : 'Activate'}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create User Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Create System User"
        description="Register a new student, faculty member, or system administrator."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          <Input
            label="Full Name"
            placeholder="Dr. Grace Hopper"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />

          <Input
            label="Email Address"
            type="email"
            placeholder="ghopper@institution.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <Input
            label="Initial Password"
            type="password"
            placeholder="StrongPassword123!"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            helperText="Minimum 8 characters."
          />

          <Select
            label="User Role"
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
            options={[
              { value: 'STUDENT', label: 'Student' },
              { value: 'FACULTY', label: 'Faculty' },
              { value: 'ADMIN', label: 'Administrator' },
            ]}
          />

          <div className="flex justify-end gap-2.5 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsAddModalOpen(false)}
              disabled={createMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" isLoading={createMutation.isPending}>
              Create Account
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
