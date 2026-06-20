<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listUsersApi, createUserApi, deleteUserApi, updateUserApi, type UserRecord } from '../../api/users'

const users = ref<UserRecord[]>([])
const loading = ref(false)

// 弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('')
const form = ref({ username: '', password: '', name: '', role: 'student' })
const editingId = ref<number | null>(null)

async function loadUsers() {
  loading.value = true
  try {
    const res = await listUsersApi()
    users.value = res.data
  } catch (e: any) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  dialogTitle.value = '新建用户'
  editingId.value = null
  form.value = { username: '', password: '', name: '', role: 'student' }
  dialogVisible.value = true
}

function openEdit(user: UserRecord) {
  dialogTitle.value = '编辑用户'
  editingId.value = user.id
  form.value = { username: user.username, password: '', name: user.name, role: user.role }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.name || !form.value.username) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    if (editingId.value) {
      await updateUserApi(editingId.value, { name: form.value.name, password: form.value.password || undefined })
      ElMessage.success('更新成功')
    } else {
      if (!form.value.password) {
        ElMessage.warning('请设置密码')
        return
      }
      await createUserApi(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await loadUsers()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '操作失败')
  }
}

async function handleDelete(id: number, name: string) {
  try {
    await ElMessageBox.confirm(`确定删除用户「${name}」吗？`, '确认删除')
    await deleteUserApi(id)
    ElMessage.success('删除成功')
    await loadUsers()
  } catch {
    // cancel
  }
}

const roleMap: Record<string, string> = { student: '学生', teacher: '教师', admin: '管理员' }
const roleColor: Record<string, string> = { student: 'tag-b', teacher: 'tag-g', admin: 'tag-o' }

onMounted(loadUsers)
</script>

<template>
  <div class="users-page">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="openCreate">+ 新建用户</el-button>
    </div>

    <el-table :data="users" v-loading="loading" stripe style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" width="140" />
      <el-table-column prop="name" label="姓名" width="140" />
      <el-table-column prop="role" label="角色" width="100">
        <template #default="{ row }">
          <span :class="['tag', roleColor[row.role] || '']">{{ roleMap[row.role] || row.role }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="password_plain" label="密码" width="140" />
      <el-table-column label="操作" min-width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id, row.name)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="460px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="!!editingId" placeholder="登录账号" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password :placeholder="editingId ? '留空不修改' : '设置密码'" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.users-page { padding: 0; }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px;
}
.page-header h2 { font-size: 18px; color: var(--color-primary); }
.tag {
  display: inline-block; padding: 2px 10px; border-radius: 12px;
  font-size: 12px; font-weight: 500;
}
.tag-b { background: #D0E3FF; color: #334EAC; }
.tag-g { background: #D1FAE5; color: #065F46; }
.tag-o { background: #FEF3C7; color: #92400E; }
</style>
