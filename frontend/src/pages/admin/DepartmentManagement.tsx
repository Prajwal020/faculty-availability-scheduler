import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { departmentsApi, DepartmentCreatePayload, DepartmentUpdatePayload } from '../../api/departments';
import { Department } from '../../types';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import {
  Building2,
  Plus,
  Edit2,
  AlertCircle,
  MapPin,
} from 'lucide-react';

export const AdminDepartmentManagement: React.FC = () => {
  const queryClient = useQueryClient();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingDept, setEditingDept] = useState<Department | null>(null);
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [building, setBuilding] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const { data: departments = [], isLoading } = useQuery({
    queryKey: ['departments'],
    queryFn: () => departmentsApi.listDepartments(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: DepartmentCreatePayload) => departmentsApi.createDepartment(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
      setIsAddModalOpen(false);
      setCode('');
      setName('');
      setBuilding('');
      setFormError(null);
    },
    onError: (err: any) => {
      setFormError(err.message || 'Failed to create department.');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: DepartmentUpdatePayload }) =>
      departmentsApi.updateDepartment(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
      setEditingDept(null);
      setFormError(null);
    },
    onError: (err: any) => {
      setFormError(err.message || 'Failed to update department.');
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!code || !name) {
      setFormError('Department code and name are required.');
      return;
    }

    setFormError(null);
    createMutation.mutate({
      code: code.trim().toUpperCase(),
      name: name.trim(),
      building: building ? building.trim() : undefined,
    });
  };

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingDept) return;

    setFormError(null);
    updateMutation.mutate({
      id: editingDept.id,
      payload: {
        code: code.trim().toUpperCase(),
        name: name.trim(),
        building: building ? building.trim() : undefined,
      },
    });
  };

  const openEdit = (dept: Department) => {
    setEditingDept(dept);
    setCode(dept.code);
    setName(dept.name);
    setBuilding(dept.building || '');
    setFormError(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Academic Departments
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Organize institutional divisions, departmental codes, and campus building allocations.
          </p>
        </div>

        <Button
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => {
            setIsAddModalOpen(true);
            setCode('');
            setName('');
            setBuilding('');
            setFormError(null);
          }}
        >
          Add Department
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-5 space-y-3">
              <CardSkeleton />
              <CardSkeleton />
            </div>
          ) : departments.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<Building2 className="w-8 h-8 text-slate-400" />}
                title="No Departments Configured"
                description="No academic departments currently exist in the institution database."
                actionLabel="Add Department"
                onAction={() => setIsAddModalOpen(true)}
              />
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {departments.map((dept) => (
                <div
                  key={dept.id}
                  className="p-5 hover:bg-slate-50/70 transition flex items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2.5">
                      <span className="text-sm font-bold text-slate-900">{dept.name}</span>
                      <span className="font-mono text-[11px] font-bold text-brand-700 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                        {dept.code}
                      </span>
                    </div>

                    {dept.building && (
                      <p className="text-xs text-slate-500 flex items-center gap-1.5">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        Building: {dept.building}
                      </p>
                    )}
                  </div>

                  <Button
                    size="sm"
                    variant="outline"
                    leftIcon={<Edit2 className="w-3.5 h-3.5" />}
                    onClick={() => openEdit(dept)}
                  >
                    Edit
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Department Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add Academic Department"
        description="Register a new academic department or school within the institution."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          <Input
            label="Department Code"
            placeholder="E.g., CS, MATH, BIO"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            required
            helperText="Short alphanumeric uppercase code (e.g. CS)"
          />

          <Input
            label="Department Name"
            placeholder="E.g., Department of Computer Science"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <Input
            label="Building / Location (optional)"
            placeholder="E.g., Turing Hall / Alan Mathison Building"
            value={building}
            onChange={(e) => setBuilding(e.target.value)}
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
              Create Department
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Department Modal */}
      {editingDept && (
        <Modal
          isOpen={!!editingDept}
          onClose={() => setEditingDept(null)}
          title="Edit Academic Department"
          description={`Update details for ${editingDept.name}.`}
        >
          <form onSubmit={handleUpdate} className="space-y-4">
            {formError && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <Input
              label="Department Code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
            />

            <Input
              label="Department Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />

            <Input
              label="Building / Location"
              value={building}
              onChange={(e) => setBuilding(e.target.value)}
            />

            <div className="flex justify-end gap-2.5 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setEditingDept(null)}
                disabled={updateMutation.isPending}
              >
                Cancel
              </Button>
              <Button type="submit" isLoading={updateMutation.isPending}>
                Save Changes
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
