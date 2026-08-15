import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { usersApi } from '../api/users';
import { useMutation } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input, Select, Textarea } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { MeetingMode } from '../types';
import { CheckCircle2, AlertCircle } from 'lucide-react';

export const Profile: React.FC = () => {
  const { user, refreshUser, isStudent, isFaculty } = useAuth();

  // Student form state
  const [major, setMajor] = useState(user?.student_profile?.major || '');
  const [studentIdNum, setStudentIdNum] = useState(user?.student_profile?.student_id_number || '');

  // Faculty form state
  const [title, setTitle] = useState(user?.faculty_profile?.title || '');
  const [officeLoc, setOfficeLoc] = useState(user?.faculty_profile?.office_location || '');
  const [bio, setBio] = useState(user?.faculty_profile?.bio || '');
  const [meetingMode, setMeetingMode] = useState<MeetingMode>(
    user?.faculty_profile?.meeting_mode || 'IN_PERSON'
  );

  const [fullName, setFullName] = useState(user?.full_name || '');
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const studentMutation = useMutation({
    mutationFn: () =>
      usersApi.updateStudentProfile({
        full_name: fullName,
        major,
        student_id_number: studentIdNum,
      }),
    onSuccess: async () => {
      await refreshUser();
      setSuccessMsg('Student profile updated successfully!');
      setErrorMsg(null);
    },
    onError: (err: any) => {
      setErrorMsg(err.message || 'Failed to update profile.');
      setSuccessMsg(null);
    },
  });

  const facultyMutation = useMutation({
    mutationFn: () =>
      usersApi.updateFacultyProfile({
        full_name: fullName,
        title,
        office_location: officeLoc,
        bio,
        meeting_mode: meetingMode,
      }),
    onSuccess: async () => {
      await refreshUser();
      setSuccessMsg('Faculty profile updated successfully!');
      setErrorMsg(null);
    },
    onError: (err: any) => {
      setErrorMsg(err.message || 'Failed to update profile.');
      setSuccessMsg(null);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg(null);
    setErrorMsg(null);

    if (isStudent) {
      studentMutation.mutate();
    } else if (isFaculty) {
      facultyMutation.mutate();
    }
  };

  const isPending = studentMutation.isPending || facultyMutation.isPending;

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Account Profile</h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Manage your personal information and institutional details.
        </p>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-brand-100 border border-brand-200 text-brand-700 font-bold text-lg flex items-center justify-center">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div>
              <CardTitle>{user?.full_name}</CardTitle>
              <p className="text-xs text-slate-500">{user?.email}</p>
            </div>
          </div>
          <Badge status={user?.role} />
        </CardHeader>

        <CardContent className="p-6">
          {successMsg && (
            <div className="mb-5 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {errorMsg && (
            <div className="mb-5 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />

            <Input label="Institutional Email" value={user?.email || ''} disabled />

            {isStudent && (
              <>
                <Input
                  label="Student ID Number"
                  value={studentIdNum}
                  onChange={(e) => setStudentIdNum(e.target.value)}
                  required
                />

                <Input
                  label="Academic Major / Field of Study"
                  value={major}
                  onChange={(e) => setMajor(e.target.value)}
                  required
                />
              </>
            )}

            {isFaculty && (
              <>
                <Input
                  label="Academic Title"
                  placeholder="E.g., Associate Professor"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />

                <Input
                  label="Office Location"
                  placeholder="E.g., Block B, Room 402"
                  value={officeLoc}
                  onChange={(e) => setOfficeLoc(e.target.value)}
                  required
                />

                <Select
                  label="Meeting Mode"
                  value={meetingMode}
                  onChange={(e) => setMeetingMode(e.target.value as MeetingMode)}
                  options={[
                    { value: 'IN_PERSON', label: 'In Person' },
                    { value: 'VIRTUAL', label: 'Virtual' },
                    { value: 'HYBRID', label: 'Hybrid' },
                  ]}
                />

                <Textarea
                  label="Biography / Research Focus"
                  placeholder="Brief description of research interests and courses taught..."
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  rows={3}
                />
              </>
            )}

            <div className="flex justify-end pt-2">
              <Button type="submit" isLoading={isPending}>
                Save Profile
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
