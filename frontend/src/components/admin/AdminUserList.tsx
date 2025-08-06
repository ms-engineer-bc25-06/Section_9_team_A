// TODO この機能は将来的に実装する(ユーザー一覧表示)
// "use client"

// import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
// import { Button } from "@/components/ui/Button"
// import { Input } from "@/components/ui/Input"
// import { Badge } from "@/components/ui/Badge"
// import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
// import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table"
// import { Search, Users, UserCheck, UserX, MoreHorizontal } from "lucide-react"
// import { useState } from "react"

// const mockUsers = [
//   {
//     id: 1,
//     name: "田中太郎",
//     email: "tanaka@company.com",
//     department: "開発部",
//     joinDate: "2023-04-01",
//     lastLogin: "2024-01-15 14:30",
//     status: "active",
//     role: "member",
//   },
//   {
//     id: 2,
//     name: "佐藤花子",
//     email: "sato@company.com",
//     department: "デザイン部",
//     joinDate: "2023-03-15",
//     lastLogin: "2024-01-15 10:15",
//     status: "active",
//     role: "member",
//   },
//   {
//     id: 3,
//     name: "鈴木一郎",
//     email: "suzuki@company.com",
//     department: "営業部",
//     joinDate: "2023-02-01",
//     lastLogin: "2024-01-14 16:45",
//     status: "inactive",
//     role: "member",
//   },
//   {
//     id: 4,
//     name: "高橋美咲",
//     email: "takahashi@company.com",
//     department: "マーケティング部",
//     joinDate: "2023-01-10",
//     lastLogin: "2024-01-15 09:20",
//     status: "active",
//     role: "admin",
//   },
// ]

// export function AdminUserList() {
//   const [searchTerm, setSearchTerm] = useState("")

//   const filteredUsers = mockUsers.filter(
//     (user) =>
//       user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
//       user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
//       user.department.toLowerCase().includes(searchTerm.toLowerCase()),
//   )

//   const getStatusBadge = (status: string) => {
//     switch (status) {
//       case "active":
//         return (
//           <Badge variant="default" className="bg-green-500">
//             アクティブ
//           </Badge>
//         )
//       case "inactive":
//         return <Badge variant="secondary">非アクティブ</Badge>
//       case "suspended":
//         return <Badge variant="destructive">停止中</Badge>
//       default:
//         return <Badge variant="secondary">不明</Badge>
//     }
//   }

//   const getRoleBadge = (role: string) => {
//     switch (role) {
//       case "admin":
//         return (
//           <Badge variant="outline" className="border-purple-500 text-purple-700">
//             管理者
//           </Badge>
//         )
//       case "member":
//         return <Badge variant="outline">メンバー</Badge>
//       default:
//         return <Badge variant="outline">不明</Badge>
//     }
//   }

//   const activeUsers = mockUsers.filter((user) => user.status === "active").length
//   const totalUsers = mockUsers.length

//   return (
//     <div className="space-y-6">
//       {/* 統計情報 */}
//       <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
//         <Card>
//           <CardHeader className="pb-3">
//             <CardTitle className="flex items-center space-x-2">
//               <Users className="h-5 w-5 text-blue-500" />
//               <span>総ユーザー数</span>
//             </CardTitle>
//           </CardHeader>
//           <CardContent>
//             <div className="text-3xl font-bold text-blue-600">{totalUsers}</div>
//           </CardContent>
//         </Card>

//         <Card>
//           <CardHeader className="pb-3">
//             <CardTitle className="flex items-center space-x-2">
//               <UserCheck className="h-5 w-5 text-green-500" />
//               <span>アクティブユーザー</span>
//             </CardTitle>
//           </CardHeader>
//           <CardContent>
//             <div className="text-3xl font-bold text-green-600">{activeUsers}</div>
//           </CardContent>
//         </Card>

//         <Card>
//           <CardHeader className="pb-3">
//             <CardTitle className="flex items-center space-x-2">
//               <UserX className="h-5 w-5 text-gray-500" />
//               <span>非アクティブユーザー</span>
//             </CardTitle>
//           </CardHeader>
//           <CardContent>
//             <div className="text-3xl font-bold text-gray-600">{totalUsers - activeUsers}</div>
//           </CardContent>
//         </Card>
//       </div>

//       {/* ユーザー一覧 */}
//       <Card>
//         <CardHeader>
//           <div className="flex justify-between items-center">
//             <CardTitle>ユーザー一覧</CardTitle>
//             <div className="relative w-64">
//               <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
//               <Input
//                 placeholder="ユーザーを検索..."
//                 value={searchTerm}
//                 onChange={(e) => setSearchTerm(e.target.value)}
//                 className="pl-10"
//               />
//             </div>
//           </div>
//         </CardHeader>
//         <CardContent>
//           <Table>
//             <TableHeader>
//               <TableRow>
//                 <TableHead>ユーザー</TableHead>
//                 <TableHead>部署</TableHead>
//                 <TableHead>入社日</TableHead>
//                 <TableHead>最終ログイン</TableHead>
//                 <TableHead>ステータス</TableHead>
//                 <TableHead>権限</TableHead>
//                 <TableHead>操作</TableHead>
//               </TableRow>
//             </TableHeader>
//             <TableBody>
//               {filteredUsers.map((user) => (
//                 <TableRow key={user.id}>
//                   <TableCell>
//                     <div className="flex items-center space-x-3">
//                       <Avatar>
//                         <AvatarImage src={`/placeholder.svg?height=32&width=32&query=${user.name}`} />
//                         <AvatarFallback>{user.name.slice(0, 2)}</AvatarFallback>
//                       </Avatar>
//                       <div>
//                         <div className="font-medium">{user.name}</div>
//                         <div className="text-sm text-gray-600">{user.email}</div>
//                       </div>
//                     </div>
//                   </TableCell>
//                   <TableCell>{user.department}</TableCell>
//                   <TableCell>{user.joinDate}</TableCell>
//                   <TableCell className="text-sm">{user.lastLogin}</TableCell>
//                   <TableCell>{getStatusBadge(user.status)}</TableCell>
//                   <TableCell>{getRoleBadge(user.role)}</TableCell>
//                   <TableCell>
//                     <Button variant="ghost" size="sm">
//                       <MoreHorizontal className="h-4 w-4" />
//                     </Button>
//                   </TableCell>
//                 </TableRow>
//               ))}
//             </TableBody>
//           </Table>
//         </CardContent>
//       </Card>
//     </div>
//   )
// }
