import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { facultyApi } from '../../api/faculty';
import { departmentsApi } from '../../api/departments';
import { Card, CardContent } from '../../components/ui/Card';
import { Input, Select } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { Search, Users, Building2, MapPin, ArrowRight } from 'lucide-react';

export const FacultyDirectory: React.FC = () => {
  const [search, setSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState<string>('ALL');

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
        fac.department_name.toLowerCase().includes(search.toLowerCase()) ||
        (fac.bio && fac.bio.toLowerCase().includes(search.toLowerCase()));

      const matchDept = selectedDept === 'ALL' || fac.department_id === selectedDept;

      return matchSearch && matchDept;
    });
  }, [facultyList, search, selectedDept]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Faculty Directory</h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Browse academic advisors and professors to schedule office hour consultations.
        </p>
      </div>

      {/* Filter & Search Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="sm:col-span-2">
              <Input
                placeholder="Search by faculty name, specialization, or keyword..."
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
                  { value: 'ALL', label: 'All Academic Departments' },
                  ...departments.map((d) => ({ value: d.id, label: `${d.name} (${d.code})` })),
                ]}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Faculty Cards Grid */}
      {isFacultyLoading || isDeptLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : filteredFaculty.length === 0 ? (
        <EmptyState
          icon={<Users className="w-7 h-7 text-slate-400" />}
          title="No Faculty Found"
          description="No faculty members matched your current filter criteria. Try adjusting your search query."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearch('');
            setSelectedDept('ALL');
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredFaculty.map((fac) => (
            <Card key={fac.id} className="flex flex-col justify-between hover:border-brand-300">
              <CardContent className="p-5 space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-11 h-11 rounded-xl bg-brand-100 border border-brand-200 text-brand-700 font-bold text-base flex items-center justify-center shrink-0">
                      {fac.full_name.charAt(0)}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 leading-snug">
                        {fac.full_name}
                      </h3>
                      <p className="text-xs text-brand-700 font-semibold">{fac.title}</p>
                    </div>
                  </div>
                  <Badge size="sm" status={fac.meeting_mode} />
                </div>

                <div className="space-y-1.5 text-xs text-slate-600 pt-1">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span className="font-medium text-slate-700">{fac.department_name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>Office: {fac.office_location}</span>
                  </div>
                </div>

                {fac.bio && (
                  <p className="text-xs text-slate-500 line-clamp-2 italic pt-1 border-t border-slate-100">
                    "{fac.bio}"
                  </p>
                )}
              </CardContent>

              <div className="p-4 bg-slate-50/60 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-slate-500 font-medium truncate max-w-[160px]">
                  {fac.email}
                </span>
                <Link to={`/student/faculty/${fac.id}`}>
                  <Button size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                    View Availability
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
