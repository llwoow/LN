# C++课程笔记总结

> **作者**: MiniMax Agent  
> **创建时间**: 2025年11月2日  
> **版本**: C++11/14/17/20/23 全面版  
> **适用对象**: C++学习者、面试准备者、程序员

---

## 📋 目录

1. [C++基础语法](#1-c基础语法)
2. [面向对象编程](#2-面向对象编程)
3. [STL标准库](#3-stl标准库)
4. [模板编程](#4-模板编程)
5. [高级特性](#5-高级特性)
6. [C++新特性](#6-c新特性)
7. [实战要点](#7-实战要点)

---

## 1. C++基础语法

### 1.1 数据类型与运算符

#### 1.1.1 基本数据类型

| 类型 | 关键字 | 大小(32位) | 大小(64位) | 取值范围 | 考点 |
|------|--------|------------|------------|----------|------|
| 字符型 | char | 1字节 | 1字节 | -128~127 | 字符编码、ASCII |
| 无符号字符 | unsigned char | 1字节 | 1字节 | 0~255 | 位运算 |
| 短整型 | short | 2字节 | 2字节 | -32768~32767 | 内存优化 |
| 无符号短整型 | unsigned short | 2字节 | 2字节 | 0~65535 | 网络编程 |
| 整型 | int | 4字节 | 4字节 | -2³¹~2³¹-1 | 默认类型 |
| 长整型 | long | 4字节 | 8字节 | 平台相关 | 跨平台问题 |
| 长长整型 | long long | 8字节 | 8字节 | -2⁶³~2⁶³-1 | C++11 |
| 单精度浮点 | float | 4字节 | 4字节 | ±3.4e±38 | 精度问题 |
| 双精度浮点 | double | 8字节 | 8字节 | ±1.7e±308 | 默认浮点 |
| 布尔型 | bool | 1字节 | 1字节 | true/false | 逻辑运算 |

#### 1.1.2 运算符优先级

<details>
<summary>点击展开运算符优先级表</summary>

| 优先级 | 运算符 | 结合性 | 说明 |
|--------|--------|--------|------|
| 1 | `()` `[]` `->` `.` `::` | 左→右 | 函数调用、数组访问 |
| 2 | `!` `~` `++` `--` `+` `-` `*` `&` `sizeof` `new` `delete` | 右→左 | 一元运算符 |
| 3 | `*` `/` `%` | 左→右 | 乘除取模 |
| 4 | `+` `-` | 左→右 | 加减 |
| 5 | `<<` `>>` | 左→右 | 位移 |
| 6 | `<` `<=` `>` `>=` | 左→右 | 关系 |
| 7 | `==` `!=` | 左→右 | 相等 |
| 8 | `&` | 左→右 | 按位与 |
| 9 | `^` | 左→右 | 按位异或 |
| 10 | `\|` | 左→右 | 按位或 |
| 11 | `&&` | 左→右 | 逻辑与 |
| 12 | `\|\|` | 左→右 | 逻辑或 |
| 13 | `?:` | 右→左 | 条件运算符 |
| 14 | `=` `+=` `-=` `*=` `/=` `%=` `&=` `^=` `\|=` `<<=` `>>=` | 右→左 | 赋值 |
| 15 | `,` | 左→右 | 逗号 |

</details>

#### 1.1.3 类型转换规则

**隐式转换规则**：

1. **整数提升**: char/short → int
2. **浮点提升**: float → double
3. **混合运算**: int + double → double
4. **数组指针**: 数组名 → 指向首元素的指针

<details>
<summary>点击展开类型转换详解</summary>

```cpp
// 整数提升示例
char c = 'A';
int i = c;  // 'A'的ASCII值65

// 浮点提升示例
float f = 3.14f;
double d = f;  // 3.140000

// 混合运算示例
int a = 5;
double b = 2.5;
double result = a + b;  // 7.5 (a被提升为double)

// 数组指针转换
int arr[5] = {1, 2, 3, 4, 5};
int* ptr = arr;  // arr退化为指向首元素的指针
```

**强制转换**：
- `static_cast`: 编译时类型转换
- `const_cast`: 去除const属性
- `reinterpret_cast`: 重新解释位模式
- `dynamic_cast`: 运行时类型检查

</details>

### 1.2 控制结构

#### 1.2.1 条件语句

```cpp
// if-else语句
if (condition1) {
    // 语句块1
} else if (condition2) {
    // 语句块2
} else {
    // 默认语句块
}

// 三元运算符
result = (condition) ? value1 : value2;

// switch语句
switch (expression) {
    case value1:
        // 语句
        break;
    case value2:
        // 语句
        break;
    default:
        // 默认语句
        break;
}
```

#### 1.2.2 循环语句

<details>
<summary>点击展开循环对比分析</summary>

| 循环类型 | 适用场景 | 特点 | 注意事项 |
|----------|----------|------|----------|
| for | 已知循环次数 | 语法简洁 | 避免修改循环变量 |
| while | 条件驱动 | 灵活 | 注意循环条件 |
| do-while | 至少执行一次 | 后判断条件 | 避免死循环 |
| range-for | 遍历容器 | C++11特性 | 只读遍历 |

```cpp
// 传统for循环
for (int i = 0; i < n; ++i) {
    // 循环体
}

// range-for循环 (C++11)
std::vector<int> vec = {1, 2, 3, 4, 5};
for (const auto& elem : vec) {
    // 只读遍历
}

// while循环
while (condition) {
    // 循环体
}

// do-while循环
do {
    // 循环体
} while (condition);
```

</details>

### 1.3 函数

#### 1.3.1 函数声明与定义

```cpp
// 函数声明
int add(int a, int b);

// 函数定义
int add(int a, int b) {
    return a + b;
}

// 默认参数
void print(int x, int base = 10) {
    // 使用base作为默认进制
}

// 函数重载
void print(int x) { print(x, 10); }
void print(double x) { print(static_cast<int>(x), 10); }
void print(const std::string& s) { std::cout << s << std::endl; }
```

#### 1.3.2 函数参数传递方式

<details>
<parameter name="click展开参数传递详解</summary>

| 传递方式 | 语法 | 效果 | 适用场景 | 注意事项 |
|----------|------|------|----------|----------|
| 值传递 | `void func(int x)` | 拷贝参数 | 小数据类型 | 拷贝开销 |
| 引用传递 | `void func(int& x)` | 直接访问 | 修改参数 | 避免临时对象 |
| 常量引用 | `void func(const int& x)` | 只读访问 | 大对象传递 | 性能最佳 |
| 指针传递 | `void func(int* x)` | 地址传递 | 可选参数 | 空指针检查 |
| 右值引用 | `void func(int&& x)` | 移动语义 | 移动构造 | C++11 |

```cpp
// 值传递
void func_by_value(int x) {
    x = 100;  // 修改副本
}

// 引用传递
void func_by_ref(int& x) {
    x = 100;  // 修改原值
}

// 常量引用传递
void func_by_const_ref(const int& x) {
    // x = 100;  // 编译错误
    std::cout << x << std::endl;
}

// 指针传递
void func_by_ptr(int* x) {
    if (x != nullptr) {
        *x = 100;
    }
}

// 右值引用 (移动语义)
void func_by_rvalue_ref(int&& x) {
    std::cout << "移动语义: " << x << std::endl;
}
```

</details>

#### 1.3.3 内联函数

```cpp
// 内联函数
inline int max(int a, int b) {
    return (a > b) ? a : b;
}

// 递归函数不能内联
inline int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);  // 递归调用无法内联
}
```

### 1.4 数组与指针

#### 1.4.1 数组

```cpp
// 一维数组
int arr[5] = {1, 2, 3, 4, 5};
int arr2[] = {1, 2, 3, 4, 5};  // 自动推导大小

// 二维数组
int matrix[3][4] = {
    {1, 2, 3, 4},
    {5, 6, 7, 8},
    {9, 10, 11, 12}
};

// 动态数组 (C++11)
std::vector<int> dynamic_arr(5, 0);  // 初始化5个0
std::array<int, 5> fixed_arr = {1, 2, 3, 4, 5};  // 固定大小数组
```

#### 1.4.2 指针

<details>
<summary>点击展开指针详解</summary>

**指针基础**：
```cpp
// 指针声明和初始化
int value = 42;
int* ptr = &value;  // ptr指向value的地址

// 解引用
int result = *ptr;  // 获取ptr指向的值

// 指针运算
ptr++;  // 指向下一个int
ptr + 2;  // 偏移2个int大小

// 指针与数组
int arr[5] = {1, 2, 3, 4, 5};
int* ptr = arr;  // arr退化为指针
int* ptr2 = &arr[0];  // 等价于上面

// 指针数组
int* ptr_arr[5];  // 5个int指针的数组
```

**指针与const**：
```cpp
int value = 42;
const int* ptr1 = &value;      // 指向常量的指针，不能通过ptr修改value
int const* ptr2 = &value;      // 等价于ptr1
int* const ptr3 = &value;      // 指针常量，ptr3不能再指向其他地址
const int* const ptr4 = &value; // 指向常量的指针常量
```

**函数指针**：
```cpp
int add(int a, int b) { return a + b; }
int subtract(int a, int b) { return a - b; }

int (*func_ptr)(int, int) = add;  // 函数指针
func_ptr = subtract;

int result = func_ptr(5, 3);  // 调用函数
```

</details>

#### 1.4.3 引用

```cpp
// 引用声明
int value = 42;
int& ref = value;  // ref是value的别名

// 引用必须初始化且不能重新绑定
ref = 100;  // 修改value的值

// 函数参数引用
void swap(int& a, int& b) {
    int temp = a;
    a = b;
    b = temp;
}

// 引用返回值
int& get_element(std::vector<int>& vec, int index) {
    return vec[index];  // 返回引用，可修改原元素
}
```

---

## 2. 面向对象编程

### 2.1 类与对象

#### 2.1.1 类定义

```cpp
class Rectangle {
private:
    double width;
    double height;
    
public:
    // 构造函数
    Rectangle(double w = 0, double h = 0) : width(w), height(h) {}
    
    // 拷贝构造函数
    Rectangle(const Rectangle& other) : width(other.width), height(other.height) {}
    
    // 移动构造函数 (C++11)
    Rectangle(Rectangle&& other) noexcept : width(other.width), height(other.height) {
        other.width = other.height = 0;
    }
    
    // 析构函数
    ~Rectangle() {}
    
    // 拷贝赋值运算符
    Rectangle& operator=(const Rectangle& other) {
        if (this != &other) {
            width = other.width;
            height = other.height;
        }
        return *this;
    }
    
    // 移动赋值运算符 (C++11)
    Rectangle& operator=(Rectangle&& other) noexcept {
        if (this != &other) {
            width = other.width;
            height = other.height;
            other.width = other.height = 0;
        }
        return *this;
    }
    
    // 成员函数
    double getArea() const { return width * height; }
    double getPerimeter() const { return 2 * (width + height); }
    
    // setter方法
    void setDimensions(double w, double h) {
        width = w;
        height = h;
    }
};
```

#### 2.1.2 访问控制

<details>
<summary>点击展开访问控制详解</summary>

| 访问修饰符 | 访问范围 | 继承影响 | 适用场景 |
|------------|----------|----------|----------|
| public | 任何地方 | 子类保持public | 接口方法 |
| protected | 类内部和子类 | 子类变为protected或public | 派生类接口 |
| private | 仅类内部 | 子类不可访问 | 内部实现 |

```cpp
class Base {
public:
    int public_member;
    
protected:
    int protected_member;
    
private:
    int private_member;
};

class Derived : public Base {
public:
    void access_members() {
        public_member = 1;      // OK
        protected_member = 2;   // OK (在派生类中)
        // private_member = 3;   // 错误! 不可访问
    }
};

int main() {
    Base obj;
    obj.public_member = 1;      // OK
    // obj.protected_member = 2; // 错误! 不可访问
    // obj.private_member = 3;   // 错误! 不可访问
}
```

</details>

### 2.2 继承

#### 2.2.1 继承方式

```cpp
// 基类
class Animal {
protected:
    std::string name;
    int age;
    
public:
    Animal(const std::string& n, int a) : name(n), age(a) {}
    
    virtual void makeSound() const {
        std::cout << name << " makes a sound" << std::endl;
    }
    
    virtual ~Animal() = default;
};

// 公有继承
class Dog : public Animal {
private:
    std::string breed;
    
public:
    Dog(const std::string& n, int a, const std::string& b) 
        : Animal(n, a), breed(b) {}
    
    void makeSound() const override {
        std::cout << name << " barks!" << std::endl;
    }
    
    void wagTail() const {
        std::cout << name << " wags tail" << std::endl;
    }
};

// 私有继承
class Cat : private Animal {
public:
    Cat(const std::string& n, int a) : Animal(n, a) {}
    
    void makeSound() const override {
        std::cout << name << " meows!" << std::endl;
    }
    
    // 通过公有方法访问基类接口
    void displayInfo() const {
        std::cout << "Cat: " << name << ", Age: " << age << std::endl;
    }
};
```

#### 2.2.2 继承中的构造函数和析构函数

<details>
<summary>点击展开继承构造函数详解</summary>

**构造函数调用顺序**：
1. 基类构造函数
2. 成员对象构造函数
3. 派生类构造函数体

**析构函数调用顺序**：
1. 派生类析构函数体
2. 成员对象析构函数
3. 基类析构函数

```cpp
class Base {
public:
    Base() { std::cout << "Base constructor" << std::endl; }
    ~Base() { std::cout << "Base destructor" << std::endl; }
};

class Member {
public:
    Member() { std::cout << "Member constructor" << std::endl; }
    ~Member() { std::cout << "Member destructor" << std::endl; }
};

class Derived : public Base {
private:
    Member member;
    
public:
    Derived() { std::cout << "Derived constructor" << std::endl; }
    ~Derived() { std::cout << "Derived destructor" << std::endl; }
};

// 输出顺序:
// Base constructor
// Member constructor  
// Derived constructor
// Derived destructor
// Member destructor
// Base destructor
```

</details>

### 2.3 多态

#### 2.3.1 虚函数

```cpp
class Shape {
protected:
    std::string color;
    
public:
    Shape(const std::string& c) : color(c) {}
    
    // 虚函数
    virtual double getArea() const = 0;  // 纯虚函数
    virtual double getPerimeter() const = 0;
    
    virtual void display() const {
        std::cout << "Color: " << color << std::endl;
    }
    
    // 虚析构函数
    virtual ~Shape() = default;
};

class Circle : public Shape {
private:
    double radius;
    
public:
    Circle(const std::string& c, double r) : Shape(c), radius(r) {}
    
    double getArea() const override {
        return M_PI * radius * radius;
    }
    
    double getPerimeter() const override {
        return 2 * M_PI * radius;
    }
    
    void display() const override {
        std::cout << "Circle - Color: " << color 
                  << ", Radius: " << radius << std::endl;
    }
};

class Rectangle : public Shape {
private:
    double width, height;
    
public:
    Rectangle(const std::string& c, double w, double h) 
        : Shape(c), width(w), height(h) {}
    
    double getArea() const override {
        return width * height;
    }
    
    double getPerimeter() const override {
        return 2 * (width + height);
    }
    
    void display() const override {
        std::cout << "Rectangle - Color: " << color 
                  << ", Width: " << width << ", Height: " << height << std::endl;
    }
};
```

#### 2.3.2 虚函数表 (vtable)

<details>
<summary>点击展开虚函数表原理</summary>

**虚函数表机制**：
1. 每个包含虚函数的类都有一个虚函数表
2. 每个对象都有一个指向虚函数表的指针(vptr)
3. 虚函数调用通过vptr间接调用

```cpp
// 虚函数表示意图
class Base {
public:
    virtual void func1() { /* ... */ }
    virtual void func2() { /* ... */ }
    virtual ~Base() {}
};

class Derived : public Base {
public:
    void func1() override { /* ... */ }  // 重写
    virtual void func3() { /* ... */ }   // 新增
};

// Base的虚函数表:
// [0] -> Base::func1()
// [1] -> Base::func2()
// [2] -> Base::~Base()

// Derived的虚函数表:
// [0] -> Derived::func1()  (重写)
// [1] -> Base::func2()     (继承)
// [2] -> Base::~Base()     (继承)
// [3] -> Derived::func3()  (新增)
```

**动态绑定过程**：
1. 通过基类指针/引用访问对象
2. 找到对象的vptr
3. 通过vptr找到对应的虚函数表
4. 在虚函数表中查找对应的函数地址
5. 调用实际对象的函数

</details>

### 2.4 抽象类与接口

#### 2.4.1 抽象类

```cpp
// 抽象类 - 包含纯虚函数
class Drawable {
public:
    virtual void draw() const = 0;  // 纯虚函数
    virtual ~Drawable() = default;
};

// 抽象类可以有具体实现
class Shape : public Drawable {
protected:
    std::string name;
    
public:
    Shape(const std::string& n) : name(n) {}
    
    // 具体实现
    void displayInfo() const {
        std::cout << "Shape: " << name << std::endl;
    }
    
    // 纯虚函数声明
    virtual double getArea() const = 0;
    virtual double getPerimeter() const = 0;
    
    // 虚函数实现
    virtual void draw() const override {
        std::cout << "Drawing " << name << std::endl;
    }
};
```

#### 2.4.2 多重继承

```cpp
class Printable {
public:
    virtual void print() const = 0;
    virtual ~Printable() = default;
};

class Serializable {
public:
    virtual void serialize(std::ostream& os) const = 0;
    virtual void deserialize(std::istream& is) = 0;
    virtual ~Serializable() = default;
};

class Document : public Printable, public Serializable {
private:
    std::string content;
    
public:
    Document(const std::string& c) : content(c) {}
    
    void print() const override {
        std::cout << "Document: " << content << std::endl;
    }
    
    void serialize(std::ostream& os) const override {
        os << content << std::endl;
    }
    
    void deserialize(std::istream& is) override {
        std::getline(is, content);
    }
};
```

---

## 3. STL标准库

### 3.1 容器概览

#### 3.1.1 序列容器

<details>
<summary>点击展开序列容器对比</summary>

| 容器 | 底层实现 | 随机访问 | 插入/删除 | 内存布局 | 适用场景 |
|------|----------|----------|-----------|----------|----------|
| vector | 动态数组 | O(1) | 末尾O(1), 其他O(n) | 连续 | 频繁随机访问 |
| deque | 双端队列 | O(1) | 两端O(1), 中间O(n) | 分段连续 | 频繁两端操作 |
| list | 双向链表 | O(n) | 已知位置O(1) | 非连续 | 频繁插入删除 |
| forward_list | 单向链表 | O(n) | 已知位置O(1) | 非连续 | 内存受限场景 |
| array | 固定数组 | O(1) | 不支持 | 连续 | 固定大小数组 |

</details>

#### 3.1.2 关联容器

| 容器 | 底层实现 | 查找 | 插入 | 删除 | 键唯一性 | 适用场景 |
|------|----------|------|------|------|----------|----------|
| set | 红黑树 | O(log n) | O(log n) | O(log n) | 是 | 唯一键集合 |
| multiset | 红黑树 | O(log n) | O(log n) | O(log n) | 否 | 重复键集合 |
| map | 红黑树 | O(log n) | O(log n) | O(log n) | 是 | 键值对 |
| multimap | 红黑树 | O(log n) | O(log n) | O(log n) | 否 | 重复键值对 |
| unordered_set | 哈希表 | 平均O(1) | 平均O(1) | 平均O(1) | 是 | 无序唯一集合 |
| unordered_map | 哈希表 | 平均O(1) | 平均O(1) | 平均O(1) | 是 | 无序键值对 |
| unordered_multiset | 哈希表 | 平均O(1) | 平均O(1) | 平均O(1) | 否 | 无序重复集合 |
| unordered_multimap | 哈希表 | 平均O(1) | 平均O(1) | 平均O(1) | 否 | 无序重复键值对 |

### 3.2 容器详解

#### 3.2.1 vector

```cpp
// vector基本操作
std::vector<int> vec;

// 构造
std::vector<int> vec1(5, 0);        // 5个0
std::vector<int> vec2(vec1.begin(), vec1.end());  // 迭代器构造
std::vector<int> vec3 = {1, 2, 3, 4, 5};  // 列表构造

// 元素访问
int first = vec[0];           // 不检查边界
int second = vec.at(1);       // 检查边界，抛出异常
int& front = vec.front();     // 第一个元素
int& back = vec.back();       // 最后一个元素
int* data = vec.data();       // 底层数组指针

// 容量操作
size_t size = vec.size();           // 元素个数
bool empty = vec.empty();           // 是否为空
size_t capacity = vec.capacity();   // 容量大小
vec.reserve(100);                   // 预留容量
vec.shrink_to_fit();                // 收缩到合适大小

// 修改操作
vec.push_back(10);          // 末尾添加
vec.pop_back();             // 末尾删除
vec.insert(vec.begin(), 5); // 迭代器位置插入
vec.erase(vec.begin());     // 删除迭代器位置元素
vec.clear();                // 清空所有元素
vec.resize(10);             // 调整大小
vec.swap(other_vec);        // 交换内容

// 迭代器
for (auto it = vec.begin(); it != vec.end(); ++it) {
    std::cout << *it << " ";
}

// C++11 range-for
for (const auto& elem : vec) {
    std::cout << elem << " ";
}
```

#### 3.2.2 map/unordered_map

<details>
<summary>点击展开map操作详解</summary>

```cpp
// map操作
std::map<std::string, int> age_map;

// 插入
age_map["Alice"] = 25;           // 使用[]操作符
age_map.insert({"Bob", 30});     // 使用insert
age_map.emplace("Charlie", 35);  // C++11原地构造

// 查找
auto it = age_map.find("Alice"); // 查找键
if (it != age_map.end()) {
    std::cout << it->first << ": " << it->second << std::endl;
}

// 访问
int alice_age = age_map["Alice"];           // 如果键不存在会插入默认值
int bob_age = age_map.at("Bob");            // 如果键不存在抛出异常

// 删除
age_map.erase("Alice");             // 通过键删除
age_map.erase(age_map.begin());     // 通过迭代器删除

// 遍历
for (const auto& pair : age_map) {
    std::cout << pair.first << ": " << pair.second << std::endl;
}

// 自定义比较函数
struct CaseInsensitiveCompare {
    bool operator()(const std::string& a, const std::string& b) const {
        return std::lexicographical_compare(a.begin(), a.end(),
                                          b.begin(), b.end(),
                                          [](char c1, char c2) {
                                              return std::tolower(c1) < std::tolower(c2);
                                          });
    }
};

std::map<std::string, int, CaseInsensitiveCompare> ci_map;
```

**unordered_map使用**：
```cpp
std::unordered_map<std::string, int> hash_map;

// 自定义哈希函数
struct MyHash {
    size_t operator()(const std::string& s) const {
        size_t hash = 0;
        for (char c : s) {
            hash = hash * 31 + c;
        }
        return hash;
    }
};

// 自定义相等函数
struct MyEqual {
    bool operator()(const std::string& a, const std::string& b) const {
        return a == b;
    }
};

std::unordered_map<std::string, int, MyHash, MyEqual> custom_hash_map;
```

</details>

### 3.3 迭代器

#### 3.3.1 迭代器类型

<details>
<summary>点击展开迭代器分类</summary>

| 迭代器类型 | 支持操作 | 容器示例 | 特点 |
|------------|----------|----------|------|
| 输入迭代器 | `++`, `*`, `==`, `!=` | istream | 只读，单向 |
| 输出迭代器 | `++`, `*` | ostream | 只写，单向 |
| 前向迭代器 | `++`, `*`, `==`, `!=` | forward_list | 读写，单向 |
| 双向迭代器 | `++`, `--`, `*`, `==`, `!=` | list, set, map | 读写，双向 |
| 随机访问迭代器 | `+`, `-`, `[]`, `<`, `>`, `<=`, `>=` | vector, deque, array | 读写，跳跃访问 |

```cpp
// 迭代器使用示例
std::vector<int> vec = {1, 2, 3, 4, 5};

// 随机访问迭代器
auto it = vec.begin();
it += 2;           // 跳跃到第3个元素
int value = it[0]; // 通过下标访问
bool less = it < vec.end(); // 随机访问比较

// 双向迭代器 (list)
std::list<int> lst = {1, 2, 3, 4, 5};
auto lit = lst.begin();
++lit;             // 前进
--lit;             // 后退

// 前向迭代器 (forward_list)
std::forward_list<int> flst = {1, 2, 3, 4, 5};
auto flit = flst.begin();
++flit;            // 只能前进
// --flit;         // 错误! 前向迭代器不能后退
```

</details>

#### 3.3.2 迭代器适配器

```cpp
// 反向迭代器
std::vector<int> vec = {1, 2, 3, 4, 5};
for (auto rit = vec.rbegin(); rit != vec.rend(); ++rit) {
    std::cout << *rit << " ";  // 输出: 5 4 3 2 1
}

// 插入迭代器
std::vector<int> vec1 = {1, 2, 3};
std::vector<int> vec2 = {10, 20};
std::copy(vec2.begin(), vec2.end(), std::back_inserter(vec1));
// vec1: {1, 2, 3, 10, 20}

// 流迭代器
std::istream_iterator<int> cin_it(std::cin);
std::istream_iterator<int> cin_end;
std::vector<int> vec((cin_it), cin_end);  // 从标准输入读取整数

std::ostream_iterator<int> cout_it(std::cout, " ");
std::copy(vec.begin(), vec.end(), cout_it);  // 输出到标准输出

// 移动迭代器 (C++11)
std::vector<std::string> vec1 = {"hello", "world"};
std::vector<std::string> vec2;
std::move(vec1.begin(), vec1.end(), std::back_inserter(vec2));
// vec1中的字符串被移动到vec2
```

### 3.4 算法

#### 3.4.1 非修改性算法

<details>
<summary>点击展开非修改性算法详解</summary>

```cpp
std::vector<int> vec = {1, 2, 3, 4, 5, 3, 2, 1};

// 查找算法
auto it = std::find(vec.begin(), vec.end(), 3);  // 查找第一个3
auto it2 = std::find_if(vec.begin(), vec.end(), [](int x) { return x > 3; });
auto it3 = std::find_if_not(vec.begin(), vec.end(), [](int x) { return x < 3; });

// 计数算法
int count = std::count(vec.begin(), vec.end(), 3);  // 统计3的个数
int count_if = std::count_if(vec.begin(), vec.end(), [](int x) { return x % 2 == 0; });

// 比较算法
bool all_positive = std::all_of(vec.begin(), vec.end(), [](int x) { return x > 0; });
bool any_negative = std::any_of(vec.begin(), vec.end(), [](int x) { return x < 0; });
bool none_zero = std::none_of(vec.begin(), vec.end(), [](int x) { return x == 0; });

// 搜索算法
std::vector<int> sub = {3, 4};
auto subrange = std::search(vec.begin(), vec.end(), sub.begin(), sub.end());
auto last_occurrence = std::find_end(vec.begin(), vec.end(), sub.begin(), sub.end());

// 最值算法
auto min_it = std::min_element(vec.begin(), vec.end());
auto max_it = std::max_element(vec.begin(), vec.end());
auto minmax_it = std::minmax_element(vec.begin(), vec.end());

// 比较算法
bool equal = std::equal(vec1.begin(), vec1.end(), vec2.begin());
auto mismatch_pair = std::mismatch(vec1.begin(), vec1.end(), vec2.begin());
```

</details>

#### 3.4.2 修改性算法

```cpp
// 变换算法
std::vector<int> vec = {1, 2, 3, 4, 5};
std::vector<int> result;
std::transform(vec.begin(), vec.end(), std::back_inserter(result), 
               [](int x) { return x * x; });  // 平方

// 替换算法
std::replace(vec.begin(), vec.end(), 3, 10);        // 替换所有3为10
std::replace_if(vec.begin(), vec.end(), [](int x) { return x % 2 == 0; }, 0);

// 删除算法
vec.erase(std::remove(vec.begin(), vec.end(), 3), vec.end());  // 删除所有3
vec.erase(std::remove_if(vec.begin(), vec.end(), [](int x) { return x > 3; }), vec.end());

// 唯一化
std::sort(vec.begin(), vec.end());
vec.erase(std::unique(vec.begin(), vec.end()), vec.end());  // 去重

// 填充和生成
std::fill(vec.begin(), vec.end(), 0);           // 填充0
std::iota(vec.begin(), vec.end(), 1);           // 填充1,2,3,4,5...

// 交换
std::swap(vec1, vec2);                          // 交换两个容器
std::iter_swap(vec1.begin(), vec2.begin());     // 交换迭代器指向的元素

// 复制和移动
std::copy(vec1.begin(), vec1.end(), vec2.begin());      // 复制
std::copy_if(vec1.begin(), vec1.end(), vec2.begin(), [](int x) { return x > 0; });
std::move(vec1.begin(), vec1.end(), vec2.begin());      // 移动
```

#### 3.4.3 排序算法

<details>
<summary>点击展开排序算法详解</summary>

```cpp
std::vector<int> vec = {5, 2, 8, 1, 9, 3, 7, 4, 6};

// 排序
std::sort(vec.begin(), vec.end());                    // 快速排序
std::stable_sort(vec.begin(), vec.end());             // 稳定排序
std::partial_sort(vec.begin(), vec.begin() + 5, vec.end());  // 部分排序

// nth_element - 将第n个元素放到正确位置
std::nth_element(vec.begin(), vec.begin() + 3, vec.end());
// 前3个元素是最小的3个(无序)，后5个是最大的5个(无序)

// 二分查找
std::sort(vec.begin(), vec.end());
bool found = std::binary_search(vec.begin(), vec.end(), 5);
auto range = std::equal_range(vec.begin(), vec.end(), 5);  // 查找相等范围

// 堆操作
std::make_heap(vec.begin(), vec.end());
std::push_heap(vec.begin(), vec.end());       // 添加元素到堆
std::pop_heap(vec.begin(), vec.end());        // 移除堆顶元素
std::sort_heap(vec.begin(), vec.end());       // 堆排序

// 合并算法
std::vector<int> vec1 = {1, 3, 5, 7, 9};
std::vector<int> vec2 = {2, 4, 6, 8, 10};
std::vector<int> merged;
std::merge(vec1.begin(), vec1.end(), vec2.begin(), vec2.end(), 
           std::back_inserter(merged));

// 集合操作
std::vector<int> set1 = {1, 2, 3, 4, 5};
std::vector<int> set2 = {3, 4, 5, 6, 7};

std::vector<int> union_set, intersection_set, difference_set;
std::set_union(set1.begin(), set1.end(), set2.begin(), set2.end(), 
               std::back_inserter(union_set));
std::set_intersection(set1.begin(), set1.end(), set2.begin(), set2.end(), 
                      std::back_inserter(intersection_set));
std::set_difference(set1.begin(), set1.end(), set2.begin(), set2.end(), 
                    std::back_inserter(difference_set));
```

</details>

### 3.5 函数对象

#### 3.5.1 预定义函数对象

```cpp
#include <functional>

// 算术函数对象
std::plus<int> plus_obj;
int result = plus_obj(3, 4);  // 7

std::minus<int> minus_obj;
int result2 = minus_obj(7, 3);  // 4

std::multiplies<int> multiplies_obj;
int result3 = multiplies_obj(3, 4);  // 12

std::divides<int> divides_obj;
int result4 = divides_obj(12, 4);  // 3

std::modulus<int> modulus_obj;
int result5 = modulus_obj(12, 5);  // 2

std::negate<int> negate_obj;
int result6 = negate_obj(5);  // -5

// 比较函数对象
std::equal_to<int> equal_to_obj;
bool eq = equal_to_obj(5, 5);  // true

std::not_equal_to<int> not_equal_to_obj;
bool neq = not_equal_to_obj(5, 3);  // true

std::greater<int> greater_obj;
bool gt = greater_obj(5, 3);  // true

std::greater_equal<int> greater_equal_obj;
bool ge = greater_equal_obj(5, 5);  // true

std::less<int> less_obj;
bool lt = less_obj(3, 5);  // true

std::less_equal<int> less_equal_obj;
bool le = less_equal_obj(5, 5);  // true

// 逻辑函数对象
std::logical_and<bool> logical_and_obj;
bool land = logical_and_obj(true, false);  // false

std::logical_or<bool> logical_or_obj;
bool lor = logical_or_obj(true, false);  // true

std::logical_not<bool> logical_not_obj;
bool lnot = logical_not_obj(true);  // false
```

#### 3.5.2 Lambda表达式

<details>
<summary>点击展开Lambda详解</summary>

**基本语法**：
```cpp
// [capture](parameters) -> return_type { body }

// 完整形式
auto lambda = [capture](int a, int b) -> int {
    return a + b;
};

// 省略返回类型 (自动推导)
auto lambda2 = [capture](int a, int b) {
    return a + b;
};

// 无参数
auto lambda3 = [capture]() {
    // body
};

// 捕获列表
[int x]              // 按值捕获x
[int &y]             // 按引用捕获y
[int x, int &y]      // 混合捕获
[=]                  // 按值捕获所有外部变量
[&]                  // 按引用捕获所有外部变量
[=, &x]              // 按值捕获所有，但x按引用
[&, =x]              // 按引用捕获所有，但x按值
[this]               // 捕获this指针 (类成员函数)
[*this]              // 捕获*this (C++17)
```

**使用示例**：
```cpp
std::vector<int> vec = {1, 2, 3, 4, 5};
int multiplier = 10;

// 按值捕获
auto lambda1 = [multiplier](int x) {
    return x * multiplier;
};

// 按引用捕获
auto lambda2 = [&multiplier](int x) {
    multiplier = 20;
    return x * multiplier;
};

// 混合捕获
int offset = 5;
auto lambda3 = [=, &multiplier](int x) {
    return x * multiplier + offset;
};

// 捕获this
class Calculator {
private:
    int base;
public:
    Calculator(int b) : base(b) {}
    
    void process() {
        std::vector<int> data = {1, 2, 3};
        
        // 捕获this指针
        std::for_each(data.begin(), data.end(), 
                     [this](int x) {
                         std::cout << x + base << " ";
                     });
        
        // C++17捕获*this
        std::for_each(data.begin(), data.end(), 
                     [*this](int x) {
                         std::cout << x + base << " ";
                     });
    }
};

// 泛型Lambda (C++14)
auto generic_lambda = [](auto x, auto y) {
    return x + y;
};
int sum = generic_lambda(1, 2);           // int
std::string str = generic_lambda(std::string("hello"), std::string(" world"));
```

**Lambda与STL算法**：
```cpp
std::vector<int> vec = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// 查找
auto it = std::find_if(vec.begin(), vec.end(), [](int x) {
    return x > 5 && x % 2 == 0;
});

// 排序
std::sort(vec.begin(), vec.end(), [](int a, int b) {
    return a > b;  // 降序
});

// 计数
int count = std::count_if(vec.begin(), vec.end(), [](int x) {
    return x % 2 == 0;
});

// 变换
std::vector<int> squares;
std::transform(vec.begin(), vec.end(), std::back_inserter(squares), 
               [](int x) { return x * x; });

// 删除
vec.erase(std::remove_if(vec.begin(), vec.end(), [](int x) {
    return x < 5;
}), vec.end());
```

</details>

---

## 4. 模板编程

### 4.1 函数模板

#### 4.1.1 基础函数模板

```cpp
// 基础函数模板
template<typename T>
T maximum(T a, T b) {
    return (a > b) ? a : b;
}

// 多个模板参数
template<typename T, typename U>
auto add(T a, U b) -> decltype(a + b) {
    return a + b;
}

// 非类型模板参数
template<typename T, int N>
class Array {
private:
    T data[N];
public:
    constexpr int size() const { return N; }
    T& operator[](int index) { return data[index]; }
    const T& operator[](int index) const { return data[index]; }
};

// 使用
int main() {
    // 函数模板实例化
    int max_int = maximum(10, 20);          // maximum<int>
    double max_double = maximum(3.14, 2.71); // maximum<double>
    
    // 显式模板参数
    int max_explicit = maximum<int>(10, 20);
    
    // 非类型模板参数
    Array<int, 5> arr;
    arr[0] = 1;
    arr[1] = 2;
    
    return 0;
}
```

#### 4.1.2 模板特化

<details>
<summary>点击展开模板特化详解</summary>

**函数模板特化**：
```cpp
// 基础模板
template<typename T>
T maximum(T a, T b) {
    return (a > b) ? a : b;
}

// 函数模板全特化
template<>
const char* maximum<const char*>(const char* a, const char* b) {
    return (strcmp(a, b) > 0) ? a : b;
}

// 函数模板偏特化 (C++14开始支持)
template<typename T>
void print(T value) {
    std::cout << "General: " << value << std::endl;
}

template<typename T>
void print<T*>(T* value) {  // 指针特化
    std::cout << "Pointer: " << *value << std::endl;
}

template<typename T>
void print<std::vector<T>>(const std::vector<T>& vec) {  // vector特化
    std::cout << "Vector: ";
    for (const auto& elem : vec) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
}
```

**类模板特化**：
```cpp
// 基础类模板
template<typename T>
class Container {
public:
    void print() const {
        std::cout << "Container of general type" << std::endl;
    }
};

// 类模板全特化
template<>
class Container<int> {
public:
    void print() const {
        std::cout << "Container of int" << std::endl;
    }
};

// 类模板偏特化
template<typename T>
class Container<T*> {  // 指针特化
public:
    void print() const {
        std::cout << "Container of pointer type" << std::endl;
    }
};

template<typename T, int N>
class Container<T[N]> {  // 数组特化
public:
    void print() const {
        std::cout << "Container of array type with size " << N << std::endl;
    }
};
```

</details>

### 4.2 类模板

#### 4.2.1 基础类模板

```cpp
// 基础类模板
template<typename T>
class SmartPointer {
private:
    T* ptr;
    
public:
    // 构造函数
    explicit SmartPointer(T* p = nullptr) : ptr(p) {}
    
    // 拷贝构造函数
    SmartPointer(const SmartPointer& other) : ptr(other.ptr) {
        if (ptr) ++ptr->ref_count;
    }
    
    // 移动构造函数 (C++11)
    SmartPointer(SmartPointer&& other) noexcept : ptr(other.ptr) {
        other.ptr = nullptr;
    }
    
    // 析构函数
    ~SmartPointer() {
        if (ptr && --ptr->ref_count == 0) {
            delete ptr;
        }
    }
    
    // 拷贝赋值运算符
    SmartPointer& operator=(const SmartPointer& other) {
        if (this != &other) {
            if (ptr && --ptr->ref_count == 0) {
                delete ptr;
            }
            ptr = other.ptr;
            if (ptr) ++ptr->ref_count;
        }
        return *this;
    }
    
    // 移动赋值运算符 (C++11)
    SmartPointer& operator=(SmartPointer&& other) noexcept {
        if (this != &other) {
            if (ptr && --ptr->ref_count == 0) {
                delete ptr;
            }
            ptr = other.ptr;
            other.ptr = nullptr;
        }
        return *this;
    }
    
    // 解引用运算符
    T& operator*() const { return *ptr; }
    T* operator->() const { return ptr; }
    
    // 布尔转换
    explicit operator bool() const { return ptr != nullptr; }
    
    // 获取原始指针
    T* get() const { return ptr; }
    
    // 重置
    void reset(T* p = nullptr) {
        if (ptr && --ptr->ref_count == 0) {
            delete ptr;
        }
        ptr = p;
        if (ptr) ++ptr->ref_count;
    }
    
    // 交换
    void swap(SmartPointer& other) {
        std::swap(ptr, other.ptr);
    }
};
```

#### 4.2.2 模板继承

```cpp
// 基础模板类
template<typename T>
class Base {
protected:
    T value;
    
public:
    Base(T v) : value(v) {}
    
    virtual void display() const {
        std::cout << "Base: " << value << std::endl;
    }
    
    virtual ~Base() = default;
};

// 派生模板类
template<typename T>
class Derived : public Base<T> {
private:
    T additional_value;
    
public:
    Derived(T v1, T v2) : Base<T>(v1), additional_value(v2) {}
    
    void display() const override {
        std::cout << "Derived: " << Base<T>::value 
                  << ", " << additional_value << std::endl;
    }
    
    void showAdditional() const {
        std::cout << "Additional: " << additional_value << std::endl;
    }
};

// 模板类的模板成员函数
template<typename T>
class Container {
private:
    std::vector<T> data;
    
public:
    void add(const T& item) {
        data.push_back(item);
    }
    
    // 模板成员函数
    template<typename Func>
    void forEach(Func func) const {
        std::for_each(data.begin(), data.end(), func);
    }
    
    // 模板成员函数特化
    template<>
    void forEach<std::ostream&>(std::ostream& os) const {
        for (const auto& item : data) {
            os << item << " ";
        }
        os << std::endl;
    }
};
```

### 4.3 高级模板特性

#### 4.3.1 SFINAE (替换失败不是错误)

<details>
<summary>点击展开SFINAE详解</summary>

**SFINAE原理**：
SFINAE是C++模板元编程的核心技术，它允许在模板参数替换失败时优雅地处理错误，而不是产生编译错误。

**使用enable_if**：
```cpp
#include <type_traits>

// 使用enable_if限制模板参数类型
template<typename T>
typename std::enable_if<std::is_integral<T>::value, T>::type
add_one(T value) {
    return value + 1;
}

template<typename T>
typename std::enable_if<std::is_floating_point<T>::value, T>::type
add_one(T value) {
    return value + 1.0;
}

// C++14简化版本
template<typename T>
std::enable_if_t<std::is_integral<T>::value, T>
add_one_v2(T value) {
    return value + 1;
}

// C++17简化版本
template<typename T>
T add_one_v3(T value) requires std::is_integral_v<T> {
    return value + 1;
}

// 使用enable_if控制函数重载
template<typename T>
void process(T value) {
    std::cout << "General processing" << std::endl;
}

template<typename T>
void process(T value) requires std::is_pointer_v<T> {
    std::cout << "Pointer processing" << std::endl;
}
```

**使用decltype和尾随返回类型**：
```cpp
template<typename T, typename U>
auto add(T a, U b) -> decltype(a + b) {
    return a + b;
}

// 更复杂的decltype用法
template<typename Container>
auto getFirst(const Container& container) 
    -> decltype(*container.begin()) {
    return *container.begin();
}

// 检查类型是否有特定成员
template<typename T>
class has_begin {
private:
    template<typename U>
    static auto check(int) -> decltype(std::declval<U>().begin(), std::true_type{});
    
    template<typename>
    static std::false_type check(...);
    
public:
    static constexpr bool value = decltype(check<T>(0))::value;
};
```

</details>

#### 4.3.2 模板模板参数

```cpp
// 模板模板参数
template<typename T, template<typename> class Container>
class Wrapper {
private:
    Container<T> data;
    
public:
    void add(const T& item) {
        data.push_back(item);
    }
    
    void display() const {
        for (const auto& item : data) {
            std::cout << item << " ";
        }
        std::cout << std::endl;
    }
};

// 使用
Wrapper<int, std::vector> vec_wrapper;
Wrapper<int, std::list> list_wrapper;

// 带默认参数的模板模板参数
template<typename T, 
         template<typename, typename> class Container = std::vector,
         typename Allocator = std::allocator<T>>
class AdvancedWrapper {
private:
    Container<T, Allocator> data;
    
public:
    void add(const T& item) {
        data.push_back(item);
    }
};
```

#### 4.3.3 变参模板

<details>
<summary>点击展开变参模板详解</summary>

**变参函数模板**：
```cpp
// 变参函数模板
template<typename... Args>
void print(Args... args) {
    // 使用展开包
    using expand = int[];
    (void)expand{0, ((void)std::cout << args << " ", 0)...};
    std::cout << std::endl;
}

// 递归展开变参模板
template<typename T>
void print_separator() {
    std::cout << std::endl;
}

template<typename T, typename... Args>
void print_separator(T first, Args... rest) {
    std::cout << first;
    if (sizeof...(Args) > 0) {
        std::cout << ", ";
    }
    print_separator(rest...);
}

// 计算变参模板参数个数
template<typename... Args>
constexpr size_t count_args() {
    return sizeof...(Args);
}

// 获取变参模板参数类型
template<typename... Args>
class TypeList {
public:
    static constexpr size_t size = sizeof...(Args);
    
    // 获取第N个类型
    template<size_t N>
    using type = typename std::tuple_element<N, std::tuple<Args...>>::type;
};

// 使用
int main() {
    print(1, 2.5, "hello", 'c');  // 输出: 1 2.5 hello c
    
    print_separator(1, 2.5, "hello", 'c');  // 输出: 1, 2.5, hello, c
    
    constexpr size_t count = count_args<int, double, std::string, char>();
    std::cout << "Count: " << count << std::endl;  // Count: 4
    
    using FirstType = TypeList<int, double, std::string>::type<0>;  // int
    using SecondType = TypeList<int, double, std::string>::type<1>; // double
    
    return 0;
}
```

**变参类模板**：
```cpp
// 变参类模板
template<typename... Args>
class Tuple {
private:
    std::tuple<Args...> data;
    
public:
    Tuple(Args... args) : data(args...) {}
    
    template<size_t N>
    auto get() const -> decltype(std::get<N>(data)) {
        return std::get<N>(data);
    }
    
    static constexpr size_t size() {
        return sizeof...(Args);
    }
};

// 变参宏
#define PRINT_ALL(...) std::cout << #__VA_ARGS__ << " = " << __VA_ARGS__ << std::endl
```

</details>

---

## 5. 高级特性

### 5.1 异常处理

#### 5.1.1 异常基础

```cpp
// 自定义异常类
class MyException : public std::exception {
private:
    std::string message;
    int error_code;
    
public:
    MyException(const std::string& msg, int code = 0) 
        : message(msg), error_code(code) {}
    
    const char* what() const noexcept override {
        return message.c_str();
    }
    
    int getErrorCode() const { return error_code; }
};

// 抛出异常
void riskyFunction(int value) {
    if (value < 0) {
        throw MyException("Negative value not allowed", -1);
    }
    if (value > 100) {
        throw std::out_of_range("Value too large");
    }
    // 正常处理
}

// 异常处理
int main() {
    try {
        riskyFunction(-5);
        riskyFunction(150);
    } catch (const MyException& e) {
        std::cerr << "MyException: " << e.what() 
                  << " (Code: " << e.getErrorCode() << ")" << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << "OutOfRange: " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
    } catch (...) {
        std::cerr << "Unknown exception occurred" << std::endl;
    }
    
    return 0;
}
```

#### 5.1.2 RAII与异常安全

<details>
<summary>点击展开RAII详解</summary>

**RAII原理**：
RAII (Resource Acquisition Is Initialization) 是C++的核心编程理念，通过对象的生命周期来管理资源的获取和释放。

```cpp
// RAII示例 - 文件管理
class FileHandler {
private:
    std::FILE* file;
    std::string filename;
    
public:
    explicit FileHandler(const std::string& fname) 
        : filename(fname), file(std::fopen(fname.c_str(), "r")) {
        if (!file) {
            throw std::runtime_error("Failed to open file: " + filename);
        }
    }
    
    ~FileHandler() {
        if (file) {
            std::fclose(file);
        }
    }
    
    // 禁止拷贝
    FileHandler(const FileHandler&) = delete;
    FileHandler& operator=(const FileHandler&) = delete;
    
    // 允许移动 (C++11)
    FileHandler(FileHandler&& other) noexcept 
        : file(other.file), filename(std::move(other.filename)) {
        other.file = nullptr;
    }
    
    FileHandler& operator=(FileHandler&& other) noexcept {
        if (this != &other) {
            if (file) {
                std::fclose(file);
            }
            file = other.file;
            filename = std::move(other.filename);
            other.file = nullptr;
        }
        return *this;
    }
    
    std::FILE* get() const { return file; }
};

// RAII示例 - 互斥锁管理
class MutexGuard {
private:
    std::mutex& mutex;
    
public:
    explicit MutexGuard(std::mutex& m) : mutex(m) {
        mutex.lock();
    }
    
    ~MutexGuard() {
        mutex.unlock();
    }
    
    // 禁止拷贝
    MutexGuard(const MutexGuard&) = delete;
    MutexGuard& operator=(const MutexGuard&) = delete;
};

// 使用RAII
std::mutex global_mutex;
int shared_counter = 0;

void safeIncrement() {
    MutexGuard guard(global_mutex);
    ++shared_counter;
    // 即使发生异常，析构函数也会自动释放锁
}
```

**异常安全保证级别**：
1. **基本保证**: 如果发生异常，对象仍然处于有效状态
2. **强保证**: 如果发生异常，操作要么完全成功，要么完全失败
3. **无异常保证**: 操作保证不抛出异常

```cpp
// 基本保证示例
class BasicGuarantee {
private:
    int* data;
    size_t size;
    
public:
    BasicGuarantee(size_t n) : data(new int[n]), size(n) {
        // 基本保证：即使初始化失败，对象仍然有效
        for (size_t i = 0; i < n; ++i) {
            data[i] = i;  // 如果这里抛出异常，对象仍然有效
        }
    }
    
    ~BasicGuarantee() {
        delete[] data;
    }
    
    void resize(size_t new_size) {
        // 基本保证：即使重新分配失败，原数据仍然有效
        int* new_data = new int[new_size];
        size_t copy_size = std::min(size, new_size);
        std::copy(data, data + copy_size, new_data);
        delete[] data;
        data = new_data;
        size = new_size;
    }
};

// 强保证示例
class StrongGuarantee {
private:
    std::vector<int> data;
    
public:
    void swap(StrongGuarantee& other) noexcept {
        // 强保证：使用noexcept确保不抛出异常
        data.swap(other.data);
    }
    
    StrongGuarantee& operator=(StrongGuarantee other) {
        // 强保证：使用拷贝-交换 idiom
        swap(other);
        return *this;
    }
};
```

</details>

### 5.2 内存管理

#### 5.2.1 智能指针

<details>
<summary>点击展开智能指针详解</summary>

**unique_ptr**：
```cpp
#include <memory>

// unique_ptr - 独占所有权
std::unique_ptr<int> ptr1(new int(42));
auto ptr2 = std::make_unique<int>(42);  // C++14推荐方式

// 独占所有权，不能拷贝，只能移动
// auto ptr3 = ptr1;  // 错误!
auto ptr3 = std::move(ptr1);  // 移动所有权

// 自定义删除器
auto deleter = [](int* p) {
    std::cout << "Deleting: " << *p << std::endl;
    delete p;
};

std::unique_ptr<int, decltype(deleter)> ptr4(new int(100), deleter);

// 数组管理
std::unique_ptr<int[]> arr(new int[5]{1, 2, 3, 4, 5});
// 或使用make_unique (C++14)
auto arr2 = std::make_unique<int[]>(5);
```

**shared_ptr**：
```cpp
// shared_ptr - 共享所有权
auto ptr1 = std::make_shared<int>(42);
auto ptr2 = ptr1;  // 引用计数增加

std::cout << "Reference count: " << ptr1.use_count() << std::endl;  // 2

// weak_ptr - 弱引用，不增加引用计数
std::weak_ptr<int> weak_ptr = ptr1;
if (auto locked_ptr = weak_ptr.lock()) {  // 检查对象是否还存在
    std::cout << *locked_ptr << std::endl;
} else {
    std::cout << "Object has been destroyed" << std::endl;
}

// 自定义删除器
auto custom_deleter = [](int* p) {
    std::cout << "Custom delete: " << *p << std::endl;
    delete p;
};

std::shared_ptr<int> ptr3(new int(100), custom_deleter);
```

**智能指针陷阱**：
```cpp
// 陷阱1: 循环引用
struct Node {
    std::shared_ptr<Node> next;
    std::shared_ptr<Node> prev;
    int value;
    
    Node(int v) : value(v) {}
    ~Node() { std::cout << "Node " << value << " destroyed" << std::endl; }
};

void circularReference() {
    auto node1 = std::make_shared<Node>(1);
    auto node2 = std::make_shared<Node>(2);
    
    node1->next = node2;
    node2->prev = node1;
    // 循环引用导致内存泄漏
}

// 解决方案：使用weak_ptr
struct SafeNode {
    std::shared_ptr<SafeNode> next;
    std::weak_ptr<SafeNode> prev;  // 使用weak_ptr
    int value;
    
    SafeNode(int v) : value(v) {}
    ~SafeNode() { std::cout << "SafeNode " << value << " destroyed" << std::endl; }
};

// 陷阱2: this指针
class SelfReference {
private:
    std::shared_ptr<SelfReference> self;
    
public:
    SelfReference() {
        // 错误：this不能直接转换为shared_ptr
        // self = std::shared_ptr<SelfReference>(this);
    }
    
    // 正确做法：使用enable_shared_from_this
};

class SafeSelfReference : public std::enable_shared_from_this<SafeSelfReference> {
public:
    std::shared_ptr<SafeSelfReference> getSelf() {
        return shared_from_this();
    }
};
```

</details>

#### 5.2.2 内存分配器

```cpp
// 自定义分配器
template<typename T>
class PoolAllocator {
private:
    struct Block {
        Block* next;
    };
    
    Block* free_list;
    std::vector<std::unique_ptr<Block[]>> chunks;
    size_t chunk_size;
    
public:
    using value_type = T;
    
    PoolAllocator(size_t chunk_size = 1024) 
        : free_list(nullptr), chunk_size(chunk_size) {}
    
    template<typename U>
    PoolAllocator(const PoolAllocator<U>& other) 
        : free_list(nullptr), chunk_size(other.chunk_size) {}
    
    T* allocate(size_t n) {
        if (n != 1) {
            throw std::bad_alloc();
        }
        
        if (!free_list) {
            allocateChunk();
        }
        
        Block* block = free_list;
        free_list = free_list->next;
        return reinterpret_cast<T*>(block);
    }
    
    void deallocate(T* p, size_t n) {
        if (n != 1) {
            return;
        }
        
        Block* block = reinterpret_cast<Block*>(p);
        block->next = free_list;
        free_list = block;
    }
    
private:
    void allocateChunk() {
        auto chunk = std::make_unique<Block[]>(chunk_size);
        chunks.push_back(std::move(chunk));
        
        // 构建自由链表
        for (size_t i = 0; i < chunk_size - 1; ++i) {
            chunks.back()[i].next = &chunks.back()[i + 1];
        }
        chunks.back()[chunk_size - 1].next = nullptr;
        
        free_list = &chunks.back()[0];
    }
};

// 使用自定义分配器
std::vector<int, PoolAllocator<int>> vec;
vec.reserve(100);
for (int i = 0; i < 100; ++i) {
    vec.push_back(i);
}
```

### 5.3 多线程编程

#### 5.3.1 std::thread

<details>
<summary>点击展开多线程详解</summary>

```cpp
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <future>

// 基本线程使用
void workerFunction(int id, int duration) {
    std::this_thread::sleep_for(std::chrono::milliseconds(duration));
    std::cout << "Worker " << id << " finished after " << duration << "ms" << std::endl;
}

int main() {
    // 创建线程
    std::thread t1(workerFunction, 1, 500);
    std::thread t2(workerFunction, 2, 300);
    
    // 等待线程完成
    t1.join();
    t2.join();
    
    return 0;
}

// Lambda线程
int main() {
    int shared_data = 0;
    
    std::thread t([&shared_data]() {
        for (int i = 0; i < 1000; ++i) {
            ++shared_data;
        }
    });
    
    t.join();
    std::cout << "Final value: " << shared_data << std::endl;
    
    return 0;
}
```

**互斥锁**：
```cpp
// 互斥锁示例
std::mutex mtx;
int shared_counter = 0;

void safeIncrement(int times) {
    for (int i = 0; i < times; ++i) {
        mtx.lock();
        ++shared_counter;
        mtx.unlock();
        
        // 或者使用lock_guard自动管理
        // std::lock_guard<std::mutex> lock(mtx);
        // ++shared_counter;
    }
}

// RAII锁管理
class Counter {
private:
    mutable std::mutex mtx;
    int value;
    
public:
    Counter() : value(0) {}
    
    void increment() {
        std::lock_guard<std::mutex> lock(mtx);
        ++value;
    }
    
    void decrement() {
        std::lock_guard<std::mutex> lock(mtx);
        --value;
    }
    
    int getValue() const {
        std::lock_guard<std::mutex> lock(mtx);
        return value;
    }
};
```

**条件变量**：
```cpp
// 生产者消费者模式
std::mutex mtx;
std::condition_variable cv;
std::queue<int> queue;
bool ready = false;

void producer() {
    for (int i = 0; i < 5; ++i) {
        std::unique_lock<std::mutex> lock(mtx);
        queue.push(i);
        std::cout << "Produced: " << i << std::endl;
        cv.notify_one();
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    {
        std::unique_lock<std::mutex> lock(mtx);
        ready = true;
    }
    cv.notify_all();
}

void consumer() {
    while (true) {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [] { return !queue.empty() || ready; });
        
        if (!queue.empty()) {
            int item = queue.front();
            queue.pop();
            std::cout << "Consumed: " << item << std::endl;
        } else if (ready) {
            break;
        }
    }
}
```

**原子操作**：
```cpp
// 原子变量
std::atomic<int> atomic_counter(0);
std::atomic<bool> atomic_flag(false);

void atomicIncrement(int times) {
    for (int i = 0; i < times; ++i) {
        atomic_counter.fetch_add(1);
    }
}

// 原子标志
void waitForFlag() {
    while (!atomic_flag.load()) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    std::cout << "Flag is set!" << std::endl;
}

void setFlag() {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    atomic_flag.store(true);
}
```

</details>

#### 5.3.2 异步编程

```cpp
#include <future>

// 异步执行
std::future<int> asyncResult = std::async(std::launch::async, []() {
    std::this_thread::sleep_for(std::chrono::seconds(2));
    return 42;
});

std::cout << "Waiting for result..." << std::endl;
int result = asyncResult.get();  // 阻塞直到结果可用
std::cout << "Result: " << result << std::endl;

// 延迟执行
std::future<int> deferredResult = std::async(std::launch::deferred, []() {
    return 100;
});

// 不会立即执行，只有调用get()时才执行
// int result2 = deferredResult.get();

// packaged_task
std::packaged_task<int(int, int)> task([](int a, int b) {
    return a + b;
});

std::future<int> taskResult = task.get_future();
std::thread(std::move(task), 10, 20).detach();
int task_output = taskResult.get();

// promise
void producer(std::promise<int> prom) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    prom.set_value(42);
}

void consumer() {
    std::promise<int> prom;
    std::future<int> fut = prom.get_future();
    
    std::thread(producer, std::move(prom)).detach();
    
    int result = fut.get();  // 阻塞等待
    std::cout << "Received: " << result << std::endl;
}
```

---

## 6. C++新特性

### 6.1 C++11新特性

#### 6.1.1 自动类型推导

```cpp
// auto关键字
auto x = 42;              // int
auto y = 3.14;            // double
auto z = "hello";         // const char*
auto w = std::vector<int>{1, 2, 3};  // std::vector<int>

// decltype关键字
int a = 10;
decltype(a) b = 20;       // int
decltype((a)) c = a;      // int& (因为(a)是左值表达式)

// decltype(auto) - C++14
decltype(auto) func1() {
    int x = 10;
    return x;  // 返回int
}

decltype(auto) func2() {
    int x = 10;
    return (x);  // 返回int& (因为(x)是左值表达式)
}
```

#### 6.1.2 初始化列表

```cpp
// 统一初始化语法
int x{42};
int y = {42};
std::vector<int> vec{1, 2, 3, 4, 5};
std::map<std::string, int> map{{"one", 1}, {"two", 2}};

// 避免窄化转换
int x{3.14};    // 编译错误 - 窄化转换
int y = 3.14;   // 警告 - 窄化转换

// 容器初始化
std::vector<int> vec1(5, 100);    // 5个100
std::vector<int> vec2{5, 100};    // 2个元素: 5和100

// 结构化绑定 - C++17
std::pair<int, std::string> getPair() {
    return {42, "hello"};
}

auto [id, name] = getPair();  // id=42, name="hello"

std::array<int, 3> getArray() {
    return {1, 2, 3};
}

auto [a, b, c] = getArray();  // a=1, b=2, c=3
```

#### 6.1.3 Lambda表达式

```cpp
// Lambda基础语法
auto lambda = [](int x, int y) { return x + y; };

// 捕获列表
int multiplier = 10;
auto lambda1 = [multiplier](int x) { return x * multiplier; };
auto lambda2 = [&multiplier](int x) { multiplier = 20; return x * multiplier; };
auto lambda3 = [=](int x) { return x * multiplier; };  // 捕获所有外部变量
auto lambda4 = [&](int x) { return x * multiplier; };  // 引用捕获所有

// 移动捕获 - C++14
std::vector<int> data = {1, 2, 3};
auto lambda5 = [data = std::move(data)](int x) { 
    return x * data.size(); 
};

// 泛型Lambda - C++14
auto generic_lambda = [](auto x, auto y) { return x + y; };
int sum = generic_lambda(1, 2);           // int
std::string str = generic_lambda(std::string("hello"), std::string(" world"));

// Lambda表达式作为参数
template<typename Func>
void process(Func f) {
    f(42);
}

process([](int x) { std::cout << x << std::endl; });
```

#### 6.1.4 右值引用和移动语义

<details>
<summary>点击展开移动语义详解</summary>

**移动语义原理**：
移动语义通过右值引用来实现，避免不必要的拷贝操作，提高性能。

```cpp
// 右值引用
int&& rvalue_ref = 42;  // 右值引用绑定到临时对象

void func(int&& x) {
    std::cout << "右值引用: " << x << std::endl;
}

func(42);  // 临时对象绑定到右值引用

// 移动构造函数
class Moveable {
private:
    int* data;
    size_t size;
    
public:
    // 移动构造函数
    Moveable(Moveable&& other) noexcept : data(other.data), size(other.size) {
        other.data = nullptr;  // 源对象被清空
        other.size = 0;
    }
    
    // 移动赋值运算符
    Moveable& operator=(Moveable&& other) noexcept {
        if (this != &other) {
            delete[] data;
            data = other.data;
            size = other.size;
            other.data = nullptr;
            other.size = 0;
        }
        return *this;
    }
    
    ~Moveable() {
        delete[] data;
    }
};

// std::move的使用
Moveable obj1;
Moveable obj2(std::move(obj1));  // 调用移动构造函数
obj2 = std::move(obj1);          // 调用移动赋值运算符

// 完美转发
template<typename T>
void wrapper(T&& arg) {
    // 保持参数的原始值类别
    func(std::forward<T>(arg));
}
```

**移动语义与STL**：
```cpp
// vector的移动操作
std::vector<int> vec1 = {1, 2, 3, 4, 5};
std::vector<int> vec2(std::move(vec1));  // 移动构造

// 避免不必要的拷贝
std::vector<int> createLargeVector() {
    std::vector<int> result(1000000, 42);
    return result;  // 移动构造（优化后）
}

std::vector<int> vec = createLargeVector();  // 移动构造

// emplace操作 - 就地构造
std::vector<std::string> vec;
vec.emplace_back("hello");        // 直接构造string
vec.push_back(std::string("hello"));  // 拷贝/移动构造
```

</details>

#### 6.1.5 智能指针

```cpp
// unique_ptr - 独占所有权
std::unique_ptr<int> ptr = std::make_unique<int>(42);
auto ptr2 = std::make_unique<std::string>("hello");

// 移动所有权
std::unique_ptr<int> ptr1 = std::make_unique<int>(10);
std::unique_ptr<int> ptr2 = std::move(ptr1);  // ptr1变为nullptr

// shared_ptr - 共享所有权
auto ptr = std::make_shared<int>(42);
auto ptr2 = ptr;  // 引用计数增加

// weak_ptr - 弱引用
std::weak_ptr<int> weak = ptr;
if (auto locked = weak.lock()) {
    std::cout << *locked << std::endl;
}

// 自定义删除器
auto deleter = [](int* p) {
    std::cout << "Deleting: " << *p << std::endl;
    delete p;
};

std::unique_ptr<int, decltype(deleter)> ptr(new int(100), deleter);
```

### 6.2 C++14新特性

#### 6.2.1 返回类型推导

```cpp
// 函数返回类型推导
auto add(int a, int b) {
    return a + b;  // 返回类型推导为int
}

auto getString() {
    return std::string("hello");  // 返回类型推导为std::string
}

// 泛型函数
template<typename T, typename U>
auto multiply(T a, U b) {
    return a * b;  // 返回类型取决于参数类型
}

// 注意事项
auto getValue() {
    if (condition) {
        return 42;  // int
    } else {
        return 3.14;  // double - 编译错误！返回类型不一致
    }
}
```

#### 6.2.2 泛型Lambda

```cpp
// 泛型Lambda参数
auto generic_func = [](auto x, auto y) {
    return x + y;
};

int sum = generic_func(1, 2);           // int + int
double dsum = generic_func(3.14, 2.71); // double + double
std::string ssum = generic_func(std::string("hello"), std::string(" world"));

// 泛型Lambda与STL
std::vector<int> vec = {1, 2, 3, 4, 5};
std::for_each(vec.begin(), vec.end(), [](auto& x) {
    x *= 2;
});

// 泛型Lambda捕获
int multiplier = 10;
auto lambda = [multiplier](auto x) {
    return x * multiplier;
};

auto result1 = lambda(5);      // 50
auto result2 = lambda(3.14);   // 31.4
```

#### 6.2.3 数字分隔符

```cpp
// 数字分隔符
int million = 1'000'000;
double pi = 3.141'592'653'589'793;
long long big_number = 9'007'199'254'740'992LL;
auto hex_number = 0xFF'FF;  // 65535

// 二进制字面量 (C++14)
int binary = 0b1010'1010;  // 170
int mask = 0b1111'1111;
```

### 6.3 C++17新特性

#### 6.3.1 结构化绑定

```cpp
// 基本用法
auto [x, y, z] = std::make_tuple(1, 2.5, "hello");

// 数组结构化绑定
int arr[3] = {1, 2, 3};
auto [a, b, c] = arr;

// 结构体结构化绑定
struct Point { int x; int y; };
Point p{10, 20};
auto [px, py] = p;

// map结构化绑定
std::map<std::string, int> map{{"key1", 10}, {"key2", 20}};
for (const auto& [key, value] : map) {
    std::cout << key << ": " << value << std::endl;
}

// 注意事项
std::pair<int, int> getPair() { return {1, 2}; }
auto [x, y] = getPair();  // x和y是const的副本，不能修改
auto& [rx, ry] = getPair();  // 错误！不能绑定到临时对象
```

#### 6.3.2 if constexpr

```cpp
// 编译时条件判断
template<typename T>
void process(T value) {
    if constexpr (std::is_integral_v<T>) {
        std::cout << "整数: " << value << std::endl;
    } else if constexpr (std::is_floating_point_v<T>) {
        std::cout << "浮点数: " << value << std::endl;
    } else {
        std::cout << "其他类型" << std::endl;
    }
}

// 避免代码膨胀
template<typename Container>
void printContainer(const Container& c) {
    if constexpr (std::is_same_v<Container, std::vector<int>>) {
        // vector<int>的特化处理
        for (int x : c) std::cout << x << " ";
    } else if constexpr (std::is_same_v<Container, std::set<int>>) {
        // set<int>的特化处理
        for (int x : c) std::cout << x << " ";
    } else {
        // 通用处理
        for (const auto& x : c) std::cout << x << " ";
    }
    std::cout << std::endl;
}
```

#### 6.3.3 std::optional

```cpp
#include <optional>

// 可选值
std::optional<int> divide(int a, int b) {
    if (b != 0) {
        return a / b;
    }
    return std::nullopt;  // 返回空值
}

// 使用
auto result = divide(10, 2);
if (result) {
    std::cout << "Result: " << *result << std::endl;
} else {
    std::cout << "Division by zero" << std::endl;
}

// 值访问
std::optional<std::string> str = "hello";
std::cout << str.value_or("default") << std::endl;  // hello
std::optional<std::string> empty;
std::cout << empty.value_or("default") << std::endl;  // default

// 链式操作
std::optional<int> opt1 = 10;
auto opt2 = opt1.map([](int x) { return x * 2; });  // opt2 = 20
auto opt3 = opt2.and_then([](int x) { 
    return x > 0 ? std::optional<int>(x + 1) : std::nullopt; 
});
```

#### 6.3.4 std::variant

```cpp
#include <variant>

// 变体类型
std::variant<int, double, std::string> value;

// 设置值
value = 42;
value = 3.14;
value = "hello";

// 访问值
if (auto* pval = std::get_if<int>(&value)) {
    std::cout << "int: " << *pval << std::endl;
} else if (auto* pval = std::get_if<double>(&value)) {
    std::cout << "double: " << *pval << std::endl;
} else if (auto* pval = std::get_if<std::string>(&value)) {
    std::cout << "string: " << *pval << std::endl;
}

// 访问器
std::visit([](auto&& arg) {
    std::cout << "Value: " << arg << std::endl;
}, value);
```

### 6.4 C++20新特性

#### 6.4.1 概念 (Concepts)

```cpp
#include <concepts>

// 基本概念
template<std::integral T>
T add(T a, T b) {
    return a + b;
}

template<std::floating_point T>
T multiply(T a, T b) {
    return a * b;
}

// 自定义概念
template<typename T>
concept Comparable = requires(T a, T b) {
    { a < b } -> std::convertible_to<bool>;
    { a > b } -> std::convertible_to<bool>;
    { a == b } -> std::convertible_to<bool>;
};

template<Comparable T>
T maxValue(T a, T b) {
    return (a > b) ? a : b;
}

// 组合概念
template<typename T>
concept Container = requires(T t) {
    typename T::value_type;
    typename T::iterator;
    { t.begin() } -> std::same_as<typename T::iterator>;
    { t.end() } -> std::same_as<typename T::iterator>;
};

template<Container C>
void printContainer(const C& c) {
    for (const auto& elem : c) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
}

// requires子句
template<typename T>
requires std::integral<T> || std::floating_point<T>
T power(T base, int exponent) {
    T result = 1;
    for (int i = 0; i < exponent; ++i) {
        result *= base;
    }
    return result;
}
```

#### 6.4.2 协程 (Coroutines)

```cpp
#include <coroutine>

// 简单的协程
struct Generator {
    struct promise_type {
        int current_value;
        
        Generator get_return_object() {
            return Generator{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        
        std::suspend_always initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        
        void unhandled_exception() { std::terminate(); }
        
        std::suspend_always yield_value(int value) {
            current_value = value;
            return {};
        }
        
        void return_void() {}
    };
    
    std::coroutine_handle<promise_type> handle;
    
    explicit Generator(std::coroutine_handle<promise_type> h) : handle(h) {}
    
    ~Generator() { if (handle) handle.destroy(); }
    
    int next() {
        handle.resume();
        return handle.promise().current_value;
    }
    
    bool done() {
        return handle.done();
    }
};

// 生成器协程
Generator simpleGenerator() {
    for (int i = 0; i < 5; ++i) {
        co_yield i;
    }
}

// 使用
int main() {
    auto gen = simpleGenerator();
    while (!gen.done()) {
        std::cout << gen.next() << " ";
    }
    return 0;
}
```

#### 6.4.3 三路比较运算符

```cpp
// 三路比较运算符
struct Point {
    int x, y;
    
    auto operator<=>(const Point&) const = default;
    
    // 或者自定义比较
    auto operator<=>(const Point& other) const {
        if (x != other.x) return x <=> other.x;
        return y <=> other.y;
    }
};

//  spaceship运算符的自动生成
struct Person {
    std::string name;
    int age;
    
    auto operator<=>(const Person&) const = default;
};

// 比较操作自动生成
bool operator==(const Person&, const Person&) = default;
bool operator!=(const Person&, const Person&) = default;
bool operator<(const Person&, const Person&) = default;
bool operator<=(const Person&, const Person&) = default;
bool operator>(const Person&, const Person&) = default;
bool operator>=(const Person&, const Person&) = default;
```

### 6.5 C++23新特性

#### 6.5.1 多维数组视图

```cpp
#include <mdspan>

// 多维数组视图
std::vector<int> data(12);
std::mdspan<int, std::extents<size_t, 3, 4>> matrix(data.data());

// 访问元素
matrix(0, 0) = 1;
matrix(1, 2) = 5;

// 访问子数组
auto row = matrix[1];
auto col = matrix.all(0, std::all);
```

#### 6.5.2 std::expected

```cpp
#include <expected>

// 期望类型 - 类似Rust的Result
std::expected<int, std::string> safeDivide(int a, int b) {
    if (b == 0) {
        return std::unexpected("Division by zero");
    }
    return a / b;
}

// 使用
auto result = safeDivide(10, 2);
if (result) {
    std::cout << "Result: " << *result << std::endl;
} else {
    std::cout << "Error: " << result.error() << std::endl;
}

// 链式操作
auto result2 = safeDivide(10, 0)
    .and_then([](int x) { return safeDivide(x, 2); })
    .transform([](int x) { return x * 2; });
```

#### 6.5.3 字符串文字作为模板参数

```cpp
// 字符串文字作为模板参数
template<std::string_view str>
constexpr void printString() {
    std::cout << str << std::endl;
}

// 使用
printString<"Hello, World!">();
printString<"Template literals in C++23">();

// 编译期字符串处理
template<std::string_view str>
constexpr size_t stringLength() {
    return str.size();
}

constexpr size_t len = stringLength<"Hello">();  // 5
```

#### 6.5.4 关联容器增强

```cpp
#include <map>
#include <set>

// 多维关联容器
std::map<std::string, std::map<int, std::string>> nested_map;
nested_map["outer"][1] = "inner";

// 范围构造和插入
std::map<int, std::string> map1 = {
    {1, "one"},
    {2, "two"},
    {3, "three"}
};

std::map<int, std::string> map2;
map2.merge(map1);  // 将map1的元素合并到map2

// 检查元素是否插入成功
auto [it, inserted] = map2.try_emplace(4, "four");
if (inserted) {
    std::cout << "Inserted successfully" << std::endl;
}
```

---

## 7. 实战要点

### 7.1 性能优化

#### 7.1.1 编译器优化

<details>
<summary>点击展开编译器优化技巧</summary>

**内联优化**：
```cpp
// 编译器可能内联的函数
inline int add(int a, int b) {
    return a + b;
}

// 编译时常量
constexpr int factorial(int n) {
    return (n <= 1) ? 1 : n * factorial(n - 1);
}

// 编译时计算
constexpr int array_size = factorial(5);  // 120
int array[array_size];
```

**编译器优化标志**：
```bash
# GCC/Clang优化
-O0  # 无优化
-O1  # 基础优化
-O2  # 常用优化 (推荐)
-O3  # 激进优化
-Ofast # 极快优化 (可能违反标准)

# 特定优化
-funroll-loops     # 循环展开
-fvectorize        # 向量化
-ftree-vectorize   # 自动向量化
-march=native      # 针对本机CPU优化
```

</details>

#### 7.1.2 内存布局优化

```cpp
// 缓存友好的数据结构
struct Point3D {
    float x, y, z;  // 连续内存，缓存友好
};

// 避免缓存未命中的结构
struct BadStructure {
    float x;
    std::vector<float> large_vector;  // 可能导致缓存未命中
    float y;
    float z;
};

// 内存池
class MemoryPool {
private:
    struct Block {
        Block* next;
        char data[1];  // 灵活数组成员
    };
    
    Block* free_list;
    size_t block_size;
    size_t pool_size;
    
public:
    MemoryPool(size_t block_size, size_t pool_size);
    ~MemoryPool();
    
    void* allocate();
    void deallocate(void* ptr);
};

// 对象池
template<typename T>
class ObjectPool {
private:
    std::vector<std::unique_ptr<T[]>> pools;
    std::queue<T*> free_objects;
    
public:
    T* acquire() {
        if (free_objects.empty()) {
            pools.emplace_back(std::make_unique<T[]>(1024));
            for (size_t i = 0; i < 1024; ++i) {
                free_objects.push(&pools.back()[i]);
            }
        }
        
        T* obj = free_objects.front();
        free_objects.pop();
        new(obj) T();  // placement new
        return obj;
    }
    
    void release(T* obj) {
        obj->~T();
        free_objects.push(obj);
    }
};
```

### 7.2 调试技巧

#### 7.2.1 调试宏

```cpp
// 调试宏
#ifdef DEBUG
    #define DEBUG_PRINT(msg) std::cout << "[DEBUG] " << msg << std::endl
    #define DEBUG_ASSERT(cond) \
        do { \
            if (!(cond)) { \
                std::cerr << "Assertion failed: " << #cond \
                          << " at " << __FILE__ << ":" << __LINE__ << std::endl; \
                std::abort(); \
            } \
        } while(0)
#else
    #define DEBUG_PRINT(msg)
    #define DEBUG_ASSERT(cond)
#endif

// 条件编译调试
void complexFunction() {
    DEBUG_PRINT("Entering complexFunction");
    
    #ifdef VERBOSE_DEBUG
    std::cout << "Processing with verbose output" << std::endl;
    #endif
    
    DEBUG_ASSERT(ptr != nullptr);
    
    DEBUG_PRINT("Exiting complexFunction");
}
```

#### 7.2.2 内存泄漏检测

```cpp
// 简单的内存泄漏检测器
class MemoryTracker {
private:
    struct Allocation {
        void* ptr;
        size_t size;
        const char* file;
        int line;
    };
    
    static std::unordered_map<void*, Allocation> allocations;
    static size_t total_allocated;
    
public:
    static void record(void* ptr, size_t size, const char* file, int line) {
        allocations[ptr] = {ptr, size, file, line};
        total_allocated += size;
    }
    
    static void deallocate(void* ptr) {
        auto it = allocations.find(ptr);
        if (it != allocations.end()) {
            total_allocated -= it->second.size;
            allocations.erase(it);
        }
    }
    
    static void report() {
        std::cout << "Memory leak report:" << std::endl;
        std::cout << "Total allocated: " << total_allocated << " bytes" << std::endl;
        std::cout << "Leaked allocations: " << allocations.size() << std::endl;
        
        for (const auto& [ptr, alloc] : allocations) {
            std::cout << "Leak: " << alloc.size << " bytes at " 
                      << alloc.file << ":" << alloc.line << std::endl;
        }
    }
    
    ~MemoryTracker() {
        if (!allocations.empty()) {
            report();
        }
    }
};

// 全局new/delete重载
void* operator new(size_t size, const char* file, int line) {
    void* ptr = malloc(size);
    MemoryTracker::record(ptr, size, file, line);
    return ptr;
}

void operator delete(void* ptr) noexcept {
    MemoryTracker::deallocate(ptr);
    free(ptr);
}

// 使用
#define new new(__FILE__, __LINE__)

int main() {
    int* ptr = new int[100];
    // int* leak = new int[1000];  // 会报告内存泄漏
    MemoryTracker::report();
    delete[] ptr;
    return 0;
}
```

### 7.3 设计模式

#### 7.3.1 单例模式

<details>
<summary>点击展开单例模式详解</summary>

**线程安全的单例**：
```cpp
// 懒汉式单例
class Singleton {
private:
    static std::atomic<Singleton*> instance;
    static std::mutex mutex;
    Singleton() = default;
    
public:
    Singleton(const Singleton&) = delete;
    Singleton& operator=(const Singleton&) = delete;
    
    static Singleton* getInstance() {
        Singleton* tmp = instance.load(std::memory_order_acquire);
        if (tmp == nullptr) {
            std::lock_guard<std::mutex> lock(mutex);
            tmp = instance.load(std::memory_order_relaxed);
            if (tmp == nullptr) {
                tmp = new Singleton();
                instance.store(tmp, std::memory_order_release);
            }
        }
        return tmp;
    }
};

// Meyers单例 (推荐)
class MeyersSingleton {
private:
    MeyersSingleton() = default;
    ~MeyersSingleton() = default;
    
public:
    MeyersSingleton(const MeyersSingleton&) = delete;
    MeyersSingleton& operator=(const MeyersSingleton&) = delete;
    
    static MeyersSingleton& getInstance() {
        static MeyersSingleton instance;  // 线程安全的局部静态变量
        return instance;
    }
};

// 模板单例
template<typename T>
class SingletonTemplate {
private:
    SingletonTemplate() = default;
    
public:
    SingletonTemplate(const SingletonTemplate&) = delete;
    SingletonTemplate& operator=(const SingletonTemplate&) = delete;
    
    static T& getInstance() {
        static T instance;
        return instance;
    }
};

class Database : public SingletonTemplate<Database> {
    // Database的单例实现
};
```

</details>

#### 7.3.2 工厂模式

```cpp
// 抽象产品
class Product {
public:
    virtual void use() = 0;
    virtual ~Product() = default;
};

// 具体产品
class ConcreteProductA : public Product {
public:
    void use() override {
        std::cout << "Using Product A" << std::endl;
    }
};

class ConcreteProductB : public Product {
public:
    void use() override {
        std::cout << "Using Product B" << std::endl;
    }
};

// 抽象工厂
class Factory {
public:
    virtual std::unique_ptr<Product> createProduct() = 0;
    virtual ~Factory() = default;
};

// 具体工厂
class FactoryA : public Factory {
public:
    std::unique_ptr<Product> createProduct() override {
        return std::make_unique<ConcreteProductA>();
    }
};

class FactoryB : public Factory {
public:
    std::unique_ptr<Product> createProduct() override {
        return std::make_unique<ConcreteProductB>();
    }
};

// 简单工厂
class SimpleFactory {
public:
    enum class ProductType { A, B };
    
    static std::unique_ptr<Product> createProduct(ProductType type) {
        switch (type) {
            case ProductType::A:
                return std::make_unique<ConcreteProductA>();
            case ProductType::B:
                return std::make_unique<ConcreteProductB>();
            default:
                return nullptr;
        }
    }
};
```

#### 7.3.3 观察者模式

```cpp
// 观察者接口
class Observer {
public:
    virtual void update(int value) = 0;
    virtual ~Observer() = default;
};

// 被观察者接口
class Subject {
public:
    virtual void attach(std::shared_ptr<Observer> observer) = 0;
    virtual void detach(std::shared_ptr<Observer> observer) = 0;
    virtual void notify() = 0;
    virtual ~Subject() = default;
};

// 具体被观察者
class ConcreteSubject : public Subject {
private:
    int state;
    std::vector<std::weak_ptr<Observer>> observers;
    
public:
    void setState(int newState) {
        state = newState;
        notify();
    }
    
    int getState() const { return state; }
    
    void attach(std::shared_ptr<Observer> observer) override {
        observers.push_back(observer);
    }
    
    void detach(std::shared_ptr<Observer> observer) override {
        observers.erase(
            std::remove_if(observers.begin(), observers.end(),
                [&observer](const auto& weak_obs) {
                    return weak_obs.expired() || weak_obs.lock() == observer;
                }),
            observers.end()
        );
    }
    
    void notify() override {
        for (auto& weak_obs : observers) {
            if (auto obs = weak_obs.lock()) {
                obs->update(state);
            }
        }
    }
};

// 具体观察者
class ConcreteObserver : public Observer {
private:
    std::string name;
    
public:
    explicit ConcreteObserver(const std::string& n) : name(n) {}
    
    void update(int value) override {
        std::cout << "Observer " << name << " received update: " << value << std::endl;
    }
};
```

### 7.4 最佳实践

#### 7.4.1 代码规范

<details>
<summary>点击展开代码规范要点</summary>

**命名规范**：
```cpp
// 变量命名 - 小写字母，下划线分隔
int user_age = 25;
std::string user_name = "John";

// 常量命名 - 全大写字母，下划线分隔
const int MAX_BUFFER_SIZE = 1024;
const std::string DEFAULT_CONFIG_FILE = "config.ini";

// 函数命名 - 小写字母，下划线分隔
void calculate_sum(int a, int b);
void print_user_info(const User& user);

// 类命名 - 大写字母开头的驼峰命名
class UserManager;
class DataProcessor;
class NetworkConnection;

// 模板参数 - T, U, V 或描述性名称
template<typename T, typename ValueType>
class Container;

// 宏定义 - 全大写字母，下划线分隔
#define MAX_RETRY_COUNT 3
#define LOG_ERROR(msg) std::cerr << "ERROR: " << msg << std::endl
```

**代码布局**：
```cpp
// 头文件保护
#ifndef USER_MANAGER_H
#define USER_MANAGER_H

#include <string>
#include <memory>

// 命名空间
namespace myapp {
namespace user {

// 类声明
class UserManager {
private:
    std::string name_;
    int age_;
    
public:
    // 构造函数
    explicit UserManager(const std::string& name);
    
    // 析构函数
    virtual ~UserManager() = default;
    
    // 拷贝和移动操作
    UserManager(const UserManager&) = default;
    UserManager& operator=(const UserManager&) = default;
    UserManager(UserManager&&) = default;
    UserManager& operator=(UserManager&&) = default;
    
    // 成员函数
    void setAge(int age);
    int getAge() const { return age_; }
    
private:
    void validateAge(int age);
};

} // namespace user
} // namespace myapp

#endif // USER_MANAGER_H
```

</details>

#### 7.4.2 错误处理策略

```cpp
// 错误处理策略

// 1. 返回错误码
enum class ErrorCode {
    Success = 0,
    InvalidInput,
    NetworkError,
    DatabaseError,
    UnknownError
};

ErrorCode processData(const std::string& data) {
    if (data.empty()) {
        return ErrorCode::InvalidInput;
    }
    // 处理逻辑
    return ErrorCode::Success;
}

// 2. 抛出异常
void processDataWithException(const std::string& data) {
    if (data.empty()) {
        throw std::invalid_argument("Data cannot be empty");
    }
    // 处理逻辑
}

// 3. 使用std::optional (C++17)
std::optional<int> parseNumber(const std::string& str) {
    try {
        return std::stoi(str);
    } catch (const std::exception&) {
        return std::nullopt;
    }
}

// 4. 使用std::expected (C++23)
std::expected<int, std::string> parseNumberExpected(const std::string& str) {
    try {
        return std::stoi(str);
    } catch (const std::exception& e) {
        return std::unexpected(e.what());
    }
}

// 5. 错误处理类
class Result {
private:
    bool success_;
    std::string error_message_;
    int value_;
    
public:
    static Result success(int value) {
        return Result(true, "", value);
    }
    
    static Result failure(const std::string& error) {
        return Result(false, error, 0);
    }
    
    bool isSuccess() const { return success_; }
    int getValue() const { return value_; }
    const std::string& getError() const { return error_message_; }
    
private:
    Result(bool success, const std::string& error, int value)
        : success_(success), error_message_(error), value_(value) {}
};
```

#### 7.4.3 测试策略

```cpp
// 单元测试示例 (使用Google Test风格)

#include <gtest/gtest.h>

class Calculator {
public:
    int add(int a, int b) { return a + b; }
    int subtract(int a, int b) { return a - b; }
    int multiply(int a, int b) { return a * b; }
    int divide(int a, int b) { 
        if (b == 0) throw std::invalid_argument("Division by zero");
        return a / b; 
    }
};

// 测试用例
TEST(CalculatorTest, AddTest) {
    Calculator calc;
    EXPECT_EQ(calc.add(2, 3), 5);
    EXPECT_EQ(calc.add(-1, 1), 0);
    EXPECT_EQ(calc.add(0, 0), 0);
}

TEST(CalculatorTest, DivideTest) {
    Calculator calc;
    EXPECT_EQ(calc.divide(10, 2), 5);
    EXPECT_THROW(calc.divide(10, 0), std::invalid_argument);
}

// 参数化测试
class MathTest : public ::testing::TestWithParam<std::tuple<int, int, int>> {
protected:
    Calculator calc;
};

TEST_P(MathTest, AddTest) {
    int a, b, expected;
    std::tie(a, b, expected) = GetParam();
    EXPECT_EQ(calc.add(a, b), expected);
}

INSTANTIATE_TEST_SUITE_P(
    AddTests,
    MathTest,
    ::testing::Values(
        std::make_tuple(1, 1, 2),
        std::make_tuple(0, 0, 0),
        std::make_tuple(-1, 1, 0),
        std::make_tuple(10, 20, 30)
    )
);
```

---

## 📝 总结

本C++课程笔记总结涵盖了从基础语法到高级特性的全面知识体系，包括：

### 🎯 核心要点

1. **基础语法掌握** - 数据类型、运算符、控制结构、函数
2. **面向对象编程** - 类、对象、继承、多态、抽象
3. **STL熟练运用** - 容器、迭代器、算法、函数对象
4. **模板编程精通** - 函数模板、类模板、SFINAE、变参模板
5. **现代C++特性** - C++11/14/17/20/23新特性
6. **实战技能** - 性能优化、调试技巧、设计模式

### 📚 学习建议

1. **循序渐进** - 从基础语法开始，逐步深入高级特性
2. **实践为主** - 多写代码，多做项目，将理论转化为实践
3. **深入理解** - 不仅要知道"怎么用"，还要理解"为什么"
4. **持续学习** - C++标准不断更新，保持学习新特性的习惯
5. **代码规范** - 养成良好的编程习惯和代码风格

### 🚀 进阶方向

- **系统编程** - 深入学习操作系统、编译器、网络编程
- **高性能计算** - 掌握并行编程、GPU编程、算法优化
- **现代C++** - 深入学习C++20/23新特性，模板元编程
- **软件工程** - 设计模式、架构设计、测试驱动开发

---

> **最后更新**: 2025年11月2日  
> **文档版本**: v1.0  
> **适用标准**: C++11/14/17/20/23

希望这份C++课程笔记总结能够帮助您系统地学习和掌握C++编程语言！