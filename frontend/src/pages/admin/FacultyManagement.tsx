import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { facultyApi } from '../../api/faculty';
import { departmentsApi } from '../../api/departments';
import { Card, CardContent } from '../../components/ui/Card';
import { Input, Select } from '../../components/ui/Input';
import { Badge } from '../../components/ui/Badge';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { Search, GraduationCap } from 'lucide-react';

export const AdminFacultyManagement: React.FC = () => {
  const [search, setSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState('ALL');

  const { data: facultyList = [], isLoading: isFacultyLoading } = useQuery({
    queryKey: ['public-faculty'],
    queryFn: () => facultyApi.listPublicFaculty(),
  });

  const { data: departments = [], isLoading: isDeptLoading } = useQuery({
    queryKey: ['departments'],
    queryFn: () => departmentsApi.listDepartments(),
  });

  const filteredFaculty = useMemo(() => {
    return facultyList.filter((fac) => {
      const matchSearch =
        fac.full_name.toLowerCase().includes(search.toLowerCase()) ||
        fac.title.toLowerCase().includes(search.toLowerCase()) ||
        fac.email.toLowerCase().includes(search.toLowerCase()) ||
        fac.department_name.toLowerCase().includes(search.toLowerCase());

      const matchDept = selectedDept === 'ALL' || fac.department_id === selectedDept;

      return matchSearch && matchDept;
    });
  }, [facultyList, search, selectedDept]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Faculty Management</h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Institutional directory of all active faculty members and their departmental associations.
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="sm:col-span-2">
              <Input
                placeholder="Search by faculty name, title, email, or department..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                leftIcon={<Search className="w-4 h-4 text-slate-400" />}
              />
            </div>
            <div>
              <Select
                value={selectedDept}
                onChange={(e) => setSelectedDept(e.target.value)}
                options={[
                  { value: 'ALL', label: 'All Departments' },
                  ...departments.map((d) => ({ value: d.id, label: `${d.name} (${d.code})` })),
                ]}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Faculty Table / Grid */}
      <Card>
        <CardContent className="p-0">
          {isFacultyLoading || isDeptLoading ? (
            <div className="p-5 space-y-3">
              <CardSkeleton />
              <CardSkeleton />
            </div>
          ) : filteredFaculty.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<GraduationCap className="w-8 h-8 text-slate-400" />}
                title="No Faculty Members Found"
                description="No faculty records matched the selected query."
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="p-4">Faculty Member</th>
                    <th className="p-4">Department</th>
                    <th className="p-4">Office & Mode</th>
                    <th className="p-4">Email</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {filteredFaculty.map((fac) => (
                    <tr key={fac.id} className="hover:bg-slate-50/70 transition">
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-brand-100 border border-brand-200 text-brand-700 font-bold flex items-center justify-center">
                            {fac.full_name.charAt(0)}
                          </div>
                          <div>
                            <p className="font-bold text-slate-900">{fac.full_name}</p>
                            <p className="text-[11px] text-slate-500">{fac.title}</p>
                          </div>
                        </div>
                      </td>

                      <td className="p-4">
                        <div className="font-semibold text-slate-800">{fac.department_name}</div>
                        <div className="text-[10px] text-slate-400">{fac.department_code}</div>
                      </td>

                      <td className="p-4">
                        <div className="space-y-1">
                          <p className="font-medium text-slate-800">{fac.office_location}</p>
                          <Badge size="sm" status={fac.meeting_mode} />
                        </div>
                      </td>

                      <td className="p-4 font-mono text-[11px] text-slate-600">{fac.email}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
