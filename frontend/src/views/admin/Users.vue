<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from "vue";
import { ElMessage } from "element-plus";
import {
  listUsersApi,
  createUserApi,
  deleteUserApi,
  updateUserApi,
  type UserRecord,
} from "../../api/users";
import { listClassesApi, type ClassInfo } from "../../api/classes";

const users = ref<UserRecord[]>([]);
const classes = ref<ClassInfo[]>([]);
const loading = ref(false);
const activeView = ref<"staff" | "students">("staff");
const search = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const selectedIds = ref<number[]>([]);
const showPwd = ref<Record<number, boolean>>({});
const showAddModal = ref(false);
const filterStaffRole = ref<"all" | "admin" | "teacher">("all");
const filterStudentClass = ref<number | null>(null);
const staffOpen = ref(true);
const studentOpen = ref(true);

const staff = computed(() =>
  users.value.filter((u) => u.role === "admin" || u.role === "teacher"),
);
const students = computed(() =>
  users.value.filter((u) => u.role === "student"),
);
const filteredStaff = computed(() => {
  let l = staff.value;
  if (filterStaffRole.value !== "all")
    l = l.filter((u) => u.role === filterStaffRole.value);
  if (search.value) {
    const q = search.value.toLowerCase();
    l = l.filter(
      (u) =>
        u.name.includes(q) ||
        u.username.includes(q) ||
        String(u.id).includes(q),
    );
  }
  return l;
});
const filteredStudents = computed(() => {
  let l = students.value;
  if (filterStudentClass.value !== null)
    l = l.filter((u) => u.class_id === filterStudentClass.value);
  if (search.value) {
    const q = search.value.toLowerCase();
    l = l.filter(
      (u) =>
        u.name.includes(q) ||
        u.username.includes(q) ||
        String(u.id).includes(q),
    );
  }
  return l;
});
const filtered = computed(() =>
  activeView.value === "staff" ? filteredStaff.value : filteredStudents.value,
);
const g3 = computed(() => classes.value.filter((c) => c.grade === "三年级"));
const g4 = computed(() => classes.value.filter((c) => c.grade === "四年级"));
const mg1 = computed(() =>
  classes.value.filter((c) => c.grade === "一年级" && c.section === "初中部"),
);
const mg2 = computed(() =>
  classes.value.filter((c) => c.grade === "二年级" && c.section === "初中部"),
);
const stats = computed(() => ({
  admin: staff.value.filter((u) => u.role === "admin").length,
  teacher: staff.value.filter((u) => u.role === "teacher").length,
  student: students.value.length,
}));

const paged = computed(() => {
  const s = (currentPage.value - 1) * pageSize.value;
  return filtered.value.slice(s, s + pageSize.value);
});
const totalPages = computed(() =>
  Math.max(1, Math.ceil(filtered.value.length / pageSize.value)),
);
const visiblePages = computed(() => {
  const t = totalPages.value;
  const cur = currentPage.value;
  if (t <= 7) return Array.from({ length: t }, (_, i) => i + 1);
  const r: (number | string)[] = [1];
  if (cur > 3) r.push("...");
  for (let i = Math.max(2, cur - 1); i <= Math.min(t - 1, cur + 1); i++)
    r.push(i);
  if (cur < t - 2) r.push("...");
  if (t > 1) r.push(t);
  return r;
});

const allSelected = computed(
  () =>
    filtered.value.length > 0 &&
    filtered.value.every((u) => selectedIds.value.includes(u.id)),
);
function toggleAll() {
  const ids = filtered.value.map((u) => u.id);
  if (allSelected.value)
    selectedIds.value = selectedIds.value.filter((id) => !ids.includes(id));
  else selectedIds.value = [...new Set([...selectedIds.value, ...ids])];
}
function toggleOne(id: number) {
  const i = selectedIds.value.indexOf(id);
  i === -1 ? selectedIds.value.push(id) : selectedIds.value.splice(i, 1);
}
function goPage(p: number) {
  currentPage.value = Math.max(1, Math.min(p, totalPages.value));
}

const form = ref({
  username: "",
  name: "",
  password: "",
  role: "teacher",
  gender: "",
  subject: "",
  class_id: null as number | null,
});
const popover = ref<{
  action: "edit" | "reset" | "delete" | null;
  user: UserRecord | null;
  value: string;
}>({ action: null, user: null, value: "" });
const popInput = ref<HTMLInputElement | null>(null);

function openPop(action: "edit" | "reset" | "delete", u: UserRecord) {
  popover.value = { action, user: u, value: action === "edit" ? u.name : "" };
  if (action === "edit")
    nextTick(() => {
      popInput.value?.focus();
      popInput.value?.select();
    });
}
function closePop() {
  popover.value.action = null;
  popover.value.user = null;
}
async function confirmPop() {
  const { action, user, value } = popover.value;
  if (!user) return;
  try {
    const ut =
      user.user_type || (user.role === "student" ? "student" : "staff");
    if (action === "edit" && value.trim() && value.trim() !== user.name) {
      await updateUserApi(user.id, { name: value.trim(), user_type: ut });
      ElMessage.success("已重命名");
      await loadData();
    } else if (action === "reset") {
      await updateUserApi(user.id, { password: "123456", user_type: ut });
      ElMessage.success("密码已重置");
      await loadData();
    } else if (action === "delete") {
      await deleteUserApi(user.id, { user_type: ut });
      ElMessage.success("已删除");
      await loadData();
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "操作失败");
  }
  closePop();
}
async function handleAdd() {
  if (!form.value.username || !form.value.name || !form.value.password) {
    ElMessage.warning("请填写完整");
    return;
  }
  try {
    if (activeView.value === "staff")
      await createUserApi({ ...form.value, role: form.value.role, class_id: form.value.class_id ?? undefined });
    else
      await createUserApi({
        ...form.value,
        role: "student",
        class_id: form.value.class_id ?? undefined,
      });
    ElMessage.success("创建成功");
    showAddModal.value = false;
    form.value = {
      username: "",
      name: "",
      password: "",
      role: "teacher",
      gender: "",
      subject: "",
      class_id: null,
    };
    await loadData();
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "创建失败");
  }
}
function togglePwd(id: number) {
  showPwd.value[id] = !showPwd.value[id];
}
function switchView(v: "staff" | "students") {
  activeView.value = v;
  currentPage.value = 1;
  search.value = "";
}
function selectStaffRole(r: "all" | "admin" | "teacher") {
  filterStaffRole.value = r;
  currentPage.value = 1;
  activeView.value = "staff";
}
function selectStudentClass(cid: number | null) {
  filterStudentClass.value = cid;
  currentPage.value = 1;
  activeView.value = "students";
}
async function loadData() {
  loading.value = true;
  try {
    const [u, c] = await Promise.all([listUsersApi(), listClassesApi()]);
    users.value = u.data;
    classes.value = c.data;
  } catch {
    ElMessage.error("加载失败");
  } finally {
    loading.value = false;
  }
}
onMounted(loadData);
</script>

<template>
  <div class="ug">
    <aside class="sb">
      <div class="sb-half">
        <div class="sh" @click="staffOpen = !staffOpen">
          <svg
            :class="['ch', { op: staffOpen }]"
            width="10"
            height="10"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <path d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          </svg>
          <span class="sd" style="background: #6366f1"></span>
          <span class="st">教职工管理</span>
          <span class="sc">{{ stats.admin + stats.teacher }}</span>
        </div>
        <div v-show="staffOpen" class="sitems">
          <div
            class="si"
            :class="{ on: activeView === 'staff' && filterStaffRole === 'all' }"
            @click="selectStaffRole('all')"
          >
            <span class="ib"></span><span class="in">全部</span
            ><span class="ic">{{ stats.admin + stats.teacher }}</span>
          </div>
          <div
            class="si"
            :class="{ on: filterStaffRole === 'admin' }"
            @click="selectStaffRole('admin')"
          >
            <span class="ib"></span><span class="in">管理员</span
            ><span class="ic">{{ stats.admin }}</span>
          </div>
          <div
            class="si"
            :class="{ on: filterStaffRole === 'teacher' }"
            @click="selectStaffRole('teacher')"
          >
            <span class="ib"></span><span class="in">教师</span
            ><span class="ic">{{ stats.teacher }}</span>
          </div>
        </div>
      </div>
      <div class="sb-half sb-bot">
        <div class="sh" @click="studentOpen = !studentOpen">
          <svg
            :class="['ch', { op: studentOpen }]"
            width="10"
            height="10"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <path d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          </svg>
          <span class="sd" style="background: var(--color-success)"></span>
          <span class="st">学生管理</span>
          <span class="sc">{{ stats.student }}</span>
        </div>
        <div v-show="studentOpen" class="sitems">
          <div
            class="si"
            :class="{
              on: activeView === 'students' && filterStudentClass === null,
            }"
            @click="selectStudentClass(null)"
          >
            <span class="ib"></span><span class="in">全部学生</span
            ><span class="ic">{{ stats.student }}</span>
          </div>
          <div
            class="si"
            style="
              font-weight: 600;
              color: #374151;
              padding-left: 24px;
              cursor: default;
            "
          >
            <span class="in">小学部</span
            ><span class="ic">{{ (g3.length + g4.length) * 30 }}</span>
          </div>
          <div
            v-for="c in g3"
            :key="'s' + c.id"
            class="si indent"
            :class="{ on: filterStudentClass === c.id }"
            @click="selectStudentClass(c.id)"
          >
            <span class="ib"></span><span class="in">{{ c.name.slice(3) }}</span
            ><span class="ic">{{ c.student_count }}</span>
          </div>
          <div
            v-for="c in g4"
            :key="'s' + c.id"
            class="si indent"
            :class="{ on: filterStudentClass === c.id }"
            @click="selectStudentClass(c.id)"
          >
            <span class="ib"></span><span class="in">{{ c.name.slice(3) }}</span
            ><span class="ic">{{ c.student_count }}</span>
          </div>
          <div
            class="si"
            style="
              font-weight: 600;
              color: #374151;
              padding-left: 24px;
              cursor: default;
            "
          >
            <span class="in">初中部</span
            ><span class="ic">{{ (mg1.length + mg2.length) * 30 }}</span>
          </div>
          <div
            v-for="c in mg1"
            :key="'m1' + c.id"
            class="si indent"
            :class="{ on: filterStudentClass === c.id }"
            @click="selectStudentClass(c.id)"
          >
            <span class="ib"></span><span class="in">{{ c.name.slice(3) }}</span
            ><span class="ic">{{ c.student_count }}</span>
          </div>
          <div
            v-for="c in mg2"
            :key="'m2' + c.id"
            class="si indent"
            :class="{ on: filterStudentClass === c.id }"
            @click="selectStudentClass(c.id)"
          >
            <span class="ib"></span><span class="in">{{ c.name.slice(3) }}</span
            ><span class="ic">{{ c.student_count }}</span>
          </div>
        </div>
      </div>
    </aside>

    <main class="mn">
      <div class="kpi">
        <div class="kc">
          <span class="kd" style="background: #6366f1"></span
          ><span class="kl">教职工</span
          ><span class="kn">{{ stats.admin + stats.teacher }}</span>
        </div>
        <div class="kc">
          <span class="kd" style="background: var(--color-danger)"></span
          ><span class="kl">管理员</span
          ><span class="kn">{{ stats.admin }}</span>
        </div>
        <div class="kc">
          <span class="kd" style="background: var(--color-primary)"></span
          ><span class="kl">教师</span
          ><span class="kn">{{ stats.teacher }}</span>
        </div>
        <div class="kc">
          <span class="kd" style="background: var(--color-success)"></span
          ><span class="kl">学生</span
          ><span class="kn">{{ stats.student }}</span>
        </div>
      </div>

      <div class="mc">
        <div class="tb">
          <div class="tt">
            <button
              :class="['tab', { on: activeView === 'staff' }]"
              @click="switchView('staff')"
            >
              教职工
            </button>
            <button
              :class="['tab', { on: activeView === 'students' }]"
              @click="switchView('students')"
            >
              学生
            </button>
          </div>
          <div class="tr">
            <input v-model="search" placeholder="搜索..." class="ts" /><button
              class="ba"
              @click="showAddModal = true"
            >
              + 添加
            </button>
          </div>
        </div>

        <div v-show="activeView === 'staff'" class="tw">
          <table class="ut">
            <thead>
              <tr>
                <th class="tc">
                  <input
                    type="checkbox"
                    :checked="allSelected"
                    @change="toggleAll"
                    class="cb"
                  />
                </th>
                <th>ID</th>
                <th>用户名</th>
                <th>姓名</th>
                <th>角色</th>
                <th>性别</th>
                <th>科目</th>
                <th>密码</th>
                <th class="ta">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="u in paged"
                :key="u.id"
                :class="['ur', { rs: selectedIds.includes(u.id) }]"
              >
                <td class="tc">
                  <input
                    type="checkbox"
                    :checked="selectedIds.includes(u.id)"
                    @change="toggleOne(u.id)"
                    class="cb"
                  />
                </td>
                <td>
                  <span class="ih">#{{ String(u.id).padStart(3, "0") }}</span>
                </td>
                <td>
                  <span class="iu">@{{ u.username }}</span>
                </td>
                <td>
                  <div class="cn">
                    <div class="av">{{ u.name[0] }}</div>
                    <span>{{ u.name }}</span>
                  </div>
                </td>
                <td>
                  <span
                    :class="[
                      'rb',
                      u.role === 'admin' ? 'role-admin' : 'role-teacher',
                    ]"
                    ><span
                      :class="[
                        'rd',
                        u.role === 'admin' ? 'dot-red' : 'dot-blue',
                      ]"
                    ></span
                    >{{ u.role === "admin" ? "管理员" : "教师" }}</span
                  >
                </td>
                <td>
                  {{
                    u.gender === "male"
                      ? "男"
                      : u.gender === "female"
                        ? "女"
                        : "-"
                  }}
                </td>
                <td>{{ u.subject || "-" }}</td>
                <td>
                  <div class="cp">
                    <span class="pt">{{
                      showPwd[u.id] ? u.password_plain : "••••••••"
                    }}</span
                    ><button class="pv" @click="togglePwd(u.id)">👁</button>
                  </div>
                </td>
                <td class="ta">
                  <div class="ac">
                    <button
                      class="ab"
                      title="改名"
                      @click="openPop($event, 'edit', u)"
                    >
                      ✏️</button
                    ><button
                      class="ab"
                      title="重置密码"
                      @click="openPop($event, 'reset', u)"
                    >
                      🔑</button
                    ><button
                      class="ab ad"
                      title="删除"
                      @click="openPop($event, 'delete', u)"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="!paged.length">
                <td colspan="9" class="em">暂无数据</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-show="activeView === 'students'" class="tw">
          <table class="ut">
            <thead>
              <tr>
                <th class="tc">
                  <input
                    type="checkbox"
                    :checked="allSelected"
                    @change="toggleAll"
                    class="cb"
                  />
                </th>
                <th>学号</th>
                <th>姓名</th>
                <th>性别</th>
                <th>班级</th>
                <th>密码</th>
                <th class="ta">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="u in paged"
                :key="u.id"
                :class="['ur', { rs: selectedIds.includes(u.id) }]"
              >
                <td class="tc">
                  <input
                    type="checkbox"
                    :checked="selectedIds.includes(u.id)"
                    @change="toggleOne(u.id)"
                    class="cb"
                  />
                </td>
                <td>
                  <span class="iu">{{ u.username }}</span>
                </td>
                <td>
                  <div class="cn">
                    <div class="av">{{ u.name[0] }}</div>
                    <span>{{ u.name }}</span>
                  </div>
                </td>
                <td>
                  {{
                    u.gender === "male"
                      ? "男"
                      : u.gender === "female"
                        ? "女"
                        : "-"
                  }}
                </td>
                <td>
                  {{ classes.find((c) => c.id === u.class_id)?.name || "-" }}
                </td>
                <td>
                  <div class="cp">
                    <span class="pt">{{
                      showPwd[u.id] ? u.password_plain : "••••••••"
                    }}</span
                    ><button class="pv" @click="togglePwd(u.id)">👁</button>
                  </div>
                </td>
                <td class="ta">
                  <div class="ac">
                    <button
                      class="ab"
                      title="改名"
                      @click="openPop($event, 'edit', u)"
                    >
                      ✏️</button
                    ><button
                      class="ab"
                      title="重置密码"
                      @click="openPop($event, 'reset', u)"
                    >
                      🔑</button
                    ><button
                      class="ab ad"
                      title="删除"
                      @click="openPop($event, 'delete', u)"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="!paged.length">
                <td colspan="7" class="em">暂无数据</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pb">
          <div class="pg">
            <button
              class="pg-btn"
              :disabled="currentPage <= 1"
              @click="goPage(currentPage - 1)"
            >
              ‹
            </button>
            <template
              v-for="(p, i) in visiblePages"
              :key="typeof p === 'number' ? p : 'dot' + i"
            >
              <button
                v-if="typeof p === 'number'"
                :class="['pg-btn', { on: p === currentPage }]"
                @click="goPage(p)"
              >
                {{ p }}
              </button>
              <span v-else class="pg-dot">…</span>
            </template>
            <button
              class="pg-btn"
              :disabled="currentPage >= totalPages"
              @click="goPage(currentPage + 1)"
            >
              ›
            </button>
          </div>
          <span class="pi"
            >{{ (currentPage - 1) * pageSize + 1 }}-{{
              Math.min(currentPage * pageSize, filtered.length)
            }}/{{ filtered.length }}</span
          >
        </div>
      </div>
    </main>

    <!-- Add Modal -->
    <Teleport to="body"
      ><div v-if="showAddModal" class="mo" @click.self="showAddModal = false">
        <div class="mb">
          <div class="mh">
            <h3>{{ activeView === "staff" ? "添加教职工" : "添加学生" }}</h3>
            <button @click="showAddModal = false" class="mx">✕</button>
          </div>
          <form @submit.prevent="handleAdd">
            <div class="ff">
              <label>用户名</label
              ><input v-model="form.username" required class="fi" />
            </div>
            <div class="ff">
              <label>姓名</label
              ><input v-model="form.name" required class="fi" />
            </div>
            <template v-if="activeView === 'staff'">
              <div class="ff">
                <label>角色</label
                ><select v-model="form.role" class="fi">
                  <option value="teacher">教师</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
              <div class="ff">
                <label>性别</label
                ><select v-model="form.gender" class="fi">
                  <option value="">不限</option>
                  <option value="male">男</option>
                  <option value="female">女</option>
                </select>
              </div>
              <div class="ff">
                <label>科目</label
                ><select v-model="form.subject" class="fi">
                  <option value="">不限</option>
                  <option value="chinese">语文</option>
                  <option value="math">数学</option>
                  <option value="english">英语</option>
                </select>
              </div>
            </template>
            <template v-else>
              <div class="ff">
                <label>性别</label
                ><select v-model="form.gender" class="fi">
                  <option value="">不限</option>
                  <option value="male">男</option>
                  <option value="female">女</option>
                </select>
              </div>
              <div class="ff">
                <label>班级</label
                ><select v-model="form.class_id" class="fi">
                  <option :value="null">选择班级</option>
                  <option v-for="c in classes" :key="c.id" :value="c.id">
                    {{ c.name }}
                  </option>
                </select>
              </div>
            </template>
            <div class="ff">
              <label>密码</label
              ><input
                v-model="form.password"
                type="password"
                required
                class="fi"
              />
            </div>
            <div class="mf">
              <button type="button" @click="showAddModal = false" class="bo">
                取消</button
              ><button type="submit" class="bs">保存</button>
            </div>
          </form>
        </div>
      </div></Teleport
    >

    <!-- Popover Modal -->
    <Teleport to="body"
      ><div v-if="popover.action" class="pop-mask" @click.self="closePop">
        <div class="pop-card">
          <template v-if="popover.action === 'edit'"
            ><div class="pop-title">重命名</div>
            <div class="pop-desc">
              新名字：<strong>{{ popover.user?.name }}</strong>
            </div>
            <input
              class="pop-input"
              v-model="popover.value"
              @keyup.enter="confirmPop"
              ref="popInput"
            />
            <div class="pop-actions">
              <button class="bo" @click="closePop">取消</button
              ><button class="bs" @click="confirmPop">保存</button>
            </div></template
          >
          <template v-else-if="popover.action === 'reset'"
            ><div class="pop-title">重置密码</div>
            <div class="pop-desc">
              将 <strong>{{ popover.user?.name }}</strong> 的密码重置为
              <code>123456</code>？
            </div>
            <div class="pop-actions">
              <button class="bo" @click="closePop">取消</button
              ><button class="bs" @click="confirmPop">重置</button>
            </div></template
          >
          <template v-else
            ><div class="pop-title pop-danger">删除确认</div>
            <div class="pop-desc">
              确定删除 <strong>{{ popover.user?.name }}</strong
              >？
            </div>
            <div class="pop-actions">
              <button class="bo" @click="closePop">取消</button
              ><button class="bd" @click="confirmPop">删除</button>
            </div></template
          >
        </div>
      </div></Teleport
    >
  </div>
</template>

<style scoped>
.ug {
  display: flex;
  gap: 0;
  min-height: calc(100vh - 130px);
  position: relative;
}
.sb {
  width: 220px;
  flex-shrink: 0;
  background: #f6f6f6;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  align-self: stretch;
}
.sb-half {
  height: 50%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.sb-bot {
  border-top: 1px solid #e5e7eb;
}
.ch {
  flex-shrink: 0;
  color: var(--color-text-light);
  transition: transform 0.2s;
}
.ch.op {
  transform: rotate(90deg);
}
.sh {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  cursor: pointer;
  user-select: none;
  flex-shrink: 0;
}
.sd {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.st {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
  flex: 1;
}
.sc {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-light);
  background: rgba(0, 0, 0, 0.04);
  padding: 1px 7px;
  border-radius: 8px;
}
.sitems {
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}
.si {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 16px 7px 28px;
  cursor: pointer;
  font-size: 12px;
  color: var(--color-text-secondary);
  transition: all 0.1s;
  user-select: none;
}
.si:hover {
  background: rgba(0, 0, 0, 0.03);
  color: var(--color-text);
}
.si.on {
  background: rgba(37, 99, 235, 0.08);
  color: var(--color-primary);
  font-weight: 600;
}
.si.indent {
  padding-left: 44px;
}
.ib {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #d1d5db;
  flex-shrink: 0;
}
.in {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ic {
  font-size: 11px;
  color: var(--color-text-light);
  flex-shrink: 0;
}
.mn {
  flex: 1;
  min-width: 0;
  margin-left: 20px;
  display: flex;
  flex-direction: column;
}
.kpi {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 20px;
}
.kc {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 14px;
  padding: 14px 18px;
}
.kl {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
}
.kn {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin-top: 6px;
}
.mc {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  flex: 1;
}
.tb {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid #f3f4f6;
  gap: 12px;
}
.tab {
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-light);
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.15s;
}
.tab.on {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}
.ts {
  padding: 6px 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  font-size: 12px;
  outline: none;
  width: 160px;
  background: #f9fafb;
}
.ba {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  border: none;
  background: var(--color-text);
  color: #fff;
  cursor: pointer;
}
.tw {
  overflow: auto;
  flex: 1;
}
.ut {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.ut thead th {
  padding: 10px 14px;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #f9fafb;
  border-bottom: 1px solid #f0f0f0;
  text-align: left;
}
.tc {
  width: 36px;
  text-align: center;
}
.ta {
  white-space: nowrap;
  width: 1%;
}
.cb {
  width: 15px;
  height: 15px;
  cursor: pointer;
  accent-color: var(--color-primary);
}
.ur {
  transition: background 0.1s;
}
.ur:hover {
  background: #f9fafb;
}
.ur.rs {
  background: #eff6ff;
}
.ut td {
  padding: 10px 14px;
  border-bottom: 1px solid #f5f5f5;
}
.cn {
  display: flex;
  align-items: center;
  gap: 8px;
}
.av {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-secondary);
}
.ih {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-light);
}
.iu {
  font-weight: 600;
  color: var(--color-text);
}
.rb {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
}
.cp {
  display: flex;
  align-items: center;
  gap: 6px;
}
.pt {
  font-family: "Courier New", monospace;
  font-size: 13px;
  letter-spacing: 1px;
  color: var(--color-text-light);
}
.pv {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-light);
  padding: 2px;
}
.ac {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s;
}
.ur:hover .ac {
  opacity: 1;
}
.ab {
  padding: 5px;
  border-radius: 5px;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--color-text-light);
  transition: all 0.15s;
  font-size: 14px;
}
.ab:hover {
  background: #f3f4f6;
  color: var(--color-primary);
}
.ad:hover {
  color: var(--color-danger);
}
.em {
  text-align: center;
  padding: 36px !important;
  color: var(--color-text-light);
}
.pb {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 18px;
  border-top: 1px solid #f5f5f5;
  flex-shrink: 0;
}
.pg {
  display: flex;
  gap: 4px;
  align-items: center;
}
.pg-btn {
  padding: 4px 10px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  background: #fff;
  color: var(--color-text-secondary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.1s;
  min-width: 28px;
  text-align: center;
}
.pg-btn.on {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}
.pg-btn:disabled {
  opacity: 0.4;
  cursor: default;
}
.pg-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  font-size: 14px;
  color: var(--color-text-light);
  letter-spacing: 2px;
  user-select: none;
}
.pi {
  font-size: 12px;
  color: var(--color-text-light);
}
.mo {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  padding: 16px;
}
.mb {
  background: #fff;
  border-radius: 14px;
  width: 100%;
  max-width: 420px;
  padding: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
.mh {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 14px;
  border-bottom: 1px solid #f0f0f0;
}
.mh h3 {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}
.ff {
  margin-bottom: 14px;
}
.ff label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 5px;
}
.fi {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
}
.mf {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 14px;
  border-top: 1px solid #f0f0f0;
  margin-top: 4px;
}
.bo {
  padding: 8px 16px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  background: #fff;
  color: var(--color-text-secondary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.bs {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: var(--color-primary);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
</style>

<style>
.pop-mask {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.pop-card {
  width: 100%;
  max-width: 360px;
  background: #fff;
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  padding: 24px;
  z-index: 2001;
}
.pop-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 6px;
}
.pop-title.pop-danger {
  color: var(--color-danger);
}
.pop-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
}
.pop-desc code {
  background: #f3f4f6;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 11px;
  font-family: var(--font-mono);
}
.pop-input {
  width: 100%;
  padding: 7px 10px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
  margin-bottom: 12px;
}
.pop-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}
.bd {
  padding: 6px 14px;
  border: none;
  border-radius: 8px;
  background: var(--color-danger);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
</style>
