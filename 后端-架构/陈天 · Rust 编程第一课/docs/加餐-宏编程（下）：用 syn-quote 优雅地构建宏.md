你好，我是陈天。

上堂课我们用最原始的方式构建了一个 RawBuilder 派生宏，本质就是从 TokenStream 中抽取需要的数据，然后生成包含目标代码的字符串，最后再把字符串转换成 TokenStream。

说到解析 TokenStream 是个苦力活，那么必然会有人做更好的工具。 [syn](https://github.com/dtolnay/syn)/ [quote](https://github.com/dtolnay/quote) 这两个库就是Rust宏生态下处理 TokenStream 的解析以及代码生成很好用的库。

今天我们就尝试用这个 syn / quote工具，来构建一个同样的 Builder 派生宏，你可以对比一下两次的具体的实现，感受 syn / quote 构建过程宏的方便之处。

## syn crate 简介

先看syn。 **syn 是一个对 TokenStream 解析的库，它提供了丰富的数据结构，对语法树中遇到的各种 Rust 语法都有支持**。

比如一个 Struct 结构，在 TokenStream 中，看到的就是一系列 TokenTree，而通过 syn 解析后，struct 的各种属性以及它的各个字段，都有明确的类型。这样，我们可以很方便地通过模式匹配来选择合适的类型进行对应的处理。

**syn 还提供了对 derive macro 的特殊支持**—— [DeriveInput](https://docs.rs/syn/latest/syn/struct.DeriveInput.html) 类型：

```rust
pub struct DeriveInput {
    pub attrs: Vec<Attribute>,
    pub vis: Visibility,
    pub ident: Ident,
    pub generics: Generics,
    pub data: Data,
}

```

通过 DeriveInput 类型，我们可以很方便地解析派生宏。比如这样：

```rust
#[proc_macro_derive(Builder)]
pub fn derive_builder(input: TokenStream) -> TokenStream {
    // Parse the input tokens into a syntax tree
    let input = parse_macro_input!(input as DeriveInput);
    ...
}

```

只需要使用 `parse_macro_input!(input as DeriveInput)`，我们就不必和 TokenStream 打交道，而是使用解析出来的 DeriveInput。上一讲我们从 TokenStream 里拿出来 struct 的名字，都费了一番功夫，这里直接访问 DeriveInput 的 ident 域就达到同样的目的，是不是非常人性化。

### Parse trait

你也许会问：为啥这个 parse\_macro\_input 有如此魔力？我也可以使用它做类似的解析么？

要回答这个问题，我们直接看代码找答案（ [来源](https://docs.rs/syn/latest/src/syn/parse_macro_input.rs.html#108-128)）：

```rust
macro_rules! parse_macro_input {
    ($tokenstream:ident as $ty:ty) => {
        match $crate::parse_macro_input::parse::<$ty>($tokenstream) {
            $crate::__private::Ok(data) => data,
            $crate::__private::Err(err) => {
                return $crate::__private::TokenStream::from(err.to_compile_error());
            }
        }
    };
    ($tokenstream:ident with $parser:path) => {
        match $crate::parse::Parser::parse($parser, $tokenstream) {
            $crate::__private::Ok(data) => data,
            $crate::__private::Err(err) => {
                return $crate::__private::TokenStream::from(err.to_compile_error());
            }
        }
    };
    ($tokenstream:ident) => {
        $crate::parse_macro_input!($tokenstream as _)
    };
}

```

结合上一讲的内容，相信你不难理解，如果我们调用 `parse_macro_input!(input as DeriveInput)`，实际上它执行了 `$crate::parse_macro_input::parse::<DeriveInput>(input)`。

那么，这个 parse 函数究竟从何而来？继续看代码（ [来源](https://docs.rs/syn/latest/src/syn/parse_macro_input.rs.html#138-152)）：

```rust
pub fn parse<T: ParseMacroInput>(token_stream: TokenStream) -> Result<T> {
    T::parse.parse(token_stream)
}

pub trait ParseMacroInput: Sized {
    fn parse(input: ParseStream) -> Result<Self>;
}

impl<T: Parse> ParseMacroInput for T {
    fn parse(input: ParseStream) -> Result<Self> {
        <T as Parse>::parse(input)
    }
}

```

从这段代码我们得知，任何实现了 ParseMacroInput trait 的类型 T，都支持 parse() 函数。进一步的， **任何 T，只要实现了 Parse trait，就自动实现了 ParseMacroInput trait**。

而这个 [Parse trait](https://docs.rs/syn/latest/syn/parse/trait.Parse.html)，就是一切魔法背后的源泉：

```rust
pub trait Parse: Sized {
    fn parse(input: ParseStream<'_>) -> Result<Self>;
}

```

syn 下面几乎所有的数据结构都实现了 Parse trait，包括 DeriveInput。所以，如果我们想自己构建一个数据结构，可以通过 `parse_macro_input!` 宏从 TokenStream 里读取内容，并写入这个数据结构， **最好的方式是为我们的数据结构实现 Parse trait**。

关于 Parse trait 的使用，今天就不深入下去了，如果你感兴趣，可以看看 DeriveInput 对 Parse 的实现（ [代码](https://docs.rs/syn/latest/src/syn/derive.rs.html#96-162)）。你也可以进一步看我们前几讲使用过的 [sqlx](https://github.com/launchbadge/sqlx) 下的 query! 宏 [内部对 Parse trait 的实现](https://github.com/launchbadge/sqlx/blob/335eed45455daf5b65b9e36d44d7f4343ba421e6/sqlx-macros/src/query/input.rs#L36-L110)。

## quote crate 简介

在宏编程的世界里， **quote 是一个特殊的原语，它把代码转换成可以操作的数据（代码即数据）**。看到这里，你是不是想到了Lisp，是的，quote 这个概念来源于 Lisp，在 Lisp 里， `(+ 1 2)` 是代码，而 `‘(+ 1 2)` 是这个代码 quote 出来的数据。

我们上一讲在生成 TokenStream 的时候，使用的是最原始的把包含代码的字符串转换成 TokenStream 的方法。这种方法虽然可以通过使用模板很好地工作，但在构建代码的过程中，我们操作的数据结构已经失去了语义。

有没有办法让我们就像撰写正常的 Rust 代码一样，保留所有的语义，然后把它们转换成 TokenStream？

有的， **可以使用 quote crate**。它提供了一个 `quote!` 宏，会替换代码中所有的 `#(...)`，生成 TokenStream。比如要写一个 hello() 方法，可以这样：

```rust
quote! {
    fn hello() {
        println!("Hello world!");
    }
}

```

这比使用字符串模板生成代码的方式更直观，功能更强大，而且保留代码的所有语义。

`quote!` 做替换的方式和 `macro_rules!` 非常类似，也支持重复匹配，一会在具体写代码的时候可以看到。

## 用 syn/quote 重写 Builder 派生宏

好，现在我们对 sync/quote 有了一个粗浅的认识，接下来就照例通过撰写代码更好地熟悉它们的功能。

怎么做，经过昨天的学习，相信你现在也比较熟悉了，大致就是 **先从 TokenStream 抽取需要的数据，再通过模板，把抽取出来的数据转换成目标代码（TokenStream）**。

由于 syn/quote 生成的 TokenStream 是 [proc-macro2](https://github.com/dtolnay/proc-macro2) 的类型，所以我们还需要使用这个库，简单说明一下proc-macro2，它是对 proc-macro 的简单封装，使用起来更方便，而且可以让过程宏可以单元测试。

我们在上一讲中创建的项目中添加更多的依赖：

```rust
[dependencies]
anyhow = "1"
askama = "0.11" # 处理 jinjia 模板，模板需要放在和 src 平行的 templates 目录下
proc-macro2 = "1" # proc-macro 的封装
quote = "1" # 用于生成代码的 TokenStream
syn = { version = "1", features = ["extra-traits"] } # 用于解析 TokenStream，使用 extra-traits 可以用于 Debug

```

注意 syn crate 默认所有数据结构都不带一些基本的 trait，比如 Debug，所以如果你想打印数据结构的话，需要使用 extra-traits feature。

### Step1：看看 DeriveInput 都输出什么？

在 [lib.rs](http://lib.rs) 中，先添加新的 Builder 派生宏：

```rust
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(Builder)]
pub fn derive_builder(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    println!("{:#?}", input);
    TokenStream::default()
}

```

通过 `parse_macro_input!`，我们得到了一个 DeriveInput 结构的数据。这里可以打印一下，看看会输出什么。

所以在 examples/command.rs 中，先为 Command 引入 Builder 宏：

```rust
use macros::{Builder, RawBuilder};

#[allow(dead_code)]
#[derive(Debug, RawBuilder, Builder)]
pub struct Command {
    executable: String,
    args: Vec<String>,
    env: Vec<String>,
    current_dir: Option<String>,
}

```

然后运行 `cargo run --example command`，就可以看到非常详尽的 DeriveInput 的输出：

- 对于 struct name，可以直接从 ident 中获取
- 对于 fields，需要从 data 内部的 DataStruct { fields } 中取。目前，我们只关心每个 field 的 ident 和 ty。

### Step2：定义自己的用于处理 derive 宏的数据结构

和上一讲一样，我们需要定义一个数据结构，来获取构建 TokenStream 用到的信息。

所以对比着上一讲，可以定义如下数据结构：

```rust
struct Fd {
    name: Ident,
    ty: Type,
		optional: bool,
}

pub struct BuilderContext {
    name: Ident,
    fields: Vec<Fd>,
}

```

### Step3：把 DeriveInput 转换成自己的数据结构

接下来要做的，就是把 DeriveInput 转换成我们需要的 BuilderContext。

所以来写两个 From trait 的实现，分别把 Field 转换成 Fd，DeriveInput 转换成 BuilderContext：

```rust
/// 把一个 Field 转换成 Fd
impl From<Field> for Fd {
    fn from(f: Field) -> Self {
        let (optional, ty) = get_option_inner(f.ty);
        Self {
            // 此时，我们拿到的是 NamedFields，所以 ident 必然存在
            name: f.ident.unwrap(),
            optional,
            ty,
        }
    }
}

/// 把 DeriveInput 转换成 BuilderContext
impl From<DeriveInput> for BuilderContext {
    fn from(input: DeriveInput) -> Self {
        let name = input.ident;

        let fields = if let Data::Struct(DataStruct {
            fields: Fields::Named(FieldsNamed { named, .. }),
            ..
        }) = input.data
        {
            named
        } else {
            panic!("Unsupported data type");
        };

        let fds = fields.into_iter().map(Fd::from).collect();
        Self { name, fields: fds }
    }
}

// 如果是 T = Option<Inner>，返回 (true, Inner)；否则返回 (false, T)
fn get_option_inner(ty: Type) -> (bool, Type) {
    todo!()
}

```

是不是简单的有点难以想象？

注意在从 input 中获取 fields 时，我们用了一个嵌套很深的模式匹配：

```rust
if let Data::Struct(DataStruct {
    fields: Fields::Named(FieldsNamed { named, .. }),
    ..
}) = input.data
{
    named
}

```

如果没有强大的模式匹配的支持，获取 FieldsNamed 会是非常冗长的代码。你可以仔细琢磨这两个 From 的实现，它很好地体现了 Rust 的优雅。

在处理 Option 类型的时候，我们用了一个还不存在的函数 get\_option\_inner()，这样一个函数是为了实现，如果是 T = Option，就返回 (true, Inner)，否则返回 (false, T)。

### Step4：使用 quote 生成代码

准备好 BuilderContext，就可以生成代码了。来写一个 render() 方法：

```rust
impl BuilderContext {
    pub fn render(&self) -> TokenStream {
        let name = &self.name;
        // 生成 XXXBuilder 的 ident
        let builder_name = Ident::new(&format!("{}Builder", name), name.span());

        let optionized_fields = self.gen_optionized_fields();
        let methods = self.gen_methods();
        let assigns = self.gen_assigns();

        quote! {
            /// Builder 结构
            #[derive(Debug, Default)]
            struct #builder_name {
                #(#optionized_fields,)*
            }

            /// Builder 结构每个字段赋值的方法，以及 build() 方法
            impl #builder_name {
                #(#methods)*

                pub fn build(mut self) -> Result<#name, &'static str> {
                    Ok(#name {
                        #(#assigns,)*
                    })
                }
            }

            /// 为使用 Builder 的原结构提供 builder() 方法，生成 Builder 结构
            impl #name {
                fn builder() -> #builder_name {
                    Default::default()
                }
            }
        }
    }

    // 为 XXXBuilder 生成 Option<T> 字段
    // 比如：executable: String -> executable: Option<String>
    fn gen_optionized_fields(&self) -> Vec<TokenStream> {
        todo!();
    }

    // 为 XXXBuilder 生成处理函数
    // 比如：methods: fn executable(mut self, v: impl Into<String>) -> Self { self.executable = Some(v); self }
    fn gen_methods(&self) -> Vec<TokenStream> {
        todo!();
    }

    // 为 XXXBuilder 生成相应的赋值语句，把 XXXBuilder 每个字段赋值给 XXX 的字段
    // 比如：#field_name: self.#field_name.take().ok_or(" xxx need to be set!")
    fn gen_assigns(&self) -> Vec<TokenStream> {
        todo!();
    }
}

```

可以看到， `quote!` 包裹的代码，和上一讲在 template 中写的代码非常类似，只不过循环的地方使用了 quote! 内部的重复语法 `#(...)*`。

到目前为止，虽然我们的代码还不能运行，但完整的从 TokenStream 到 TokenStream 转换的骨架已经完成，剩下的只是实现细节而已，你可以试着自己实现。

### Step5：完整实现

好，我们创建 src/builder.rs 文件（记得在 src/lib.rs 里引入），然后写入代码：

```rust
use proc_macro2::{Ident, TokenStream};
use quote::quote;
use syn::{
    Data, DataStruct, DeriveInput, Field, Fields, FieldsNamed, GenericArgument, Path, Type,
    TypePath,
};

/// 我们需要的描述一个字段的所有信息
struct Fd {
    name: Ident,
    ty: Type,
    optional: bool,
}

/// 我们需要的描述一个 struct 的所有信息
pub struct BuilderContext {
    name: Ident,
    fields: Vec<Fd>,
}

/// 把一个 Field 转换成 Fd
impl From<Field> for Fd {
    fn from(f: Field) -> Self {
        let (optional, ty) = get_option_inner(&f.ty);
        Self {
            // 此时，我们拿到的是 NamedFields，所以 ident 必然存在
            name: f.ident.unwrap(),
            optional,
            ty: ty.to_owned(),
        }
    }
}

/// 把 DeriveInput 转换成 BuilderContext
impl From<DeriveInput> for BuilderContext {
    fn from(input: DeriveInput) -> Self {
        let name = input.ident;

        let fields = if let Data::Struct(DataStruct {
            fields: Fields::Named(FieldsNamed { named, .. }),
            ..
        }) = input.data
        {
            named
        } else {
            panic!("Unsupported data type");
        };

        let fds = fields.into_iter().map(Fd::from).collect();
        Self { name, fields: fds }
    }
}

impl BuilderContext {
    pub fn render(&self) -> TokenStream {
        let name = &self.name;
        // 生成 XXXBuilder 的 ident
        let builder_name = Ident::new(&format!("{}Builder", name), name.span());

        let optionized_fields = self.gen_optionized_fields();
        let methods = self.gen_methods();
        let assigns = self.gen_assigns();

        quote! {
            /// Builder 结构
            #[derive(Debug, Default)]
            struct #builder_name {
                #(#optionized_fields,)*
            }

            /// Builder 结构每个字段赋值的方法，以及 build() 方法
            impl #builder_name {
                #(#methods)*

                pub fn build(mut self) -> Result<#name, &'static str> {
                    Ok(#name {
                        #(#assigns,)*
                    })
                }
            }

            /// 为使用 Builder 的原结构提供 builder() 方法，生成 Builder 结构
            impl #name {
                fn builder() -> #builder_name {
                    Default::default()
                }
            }
        }
    }

    // 为 XXXBuilder 生成 Option<T> 字段
    // 比如：executable: String -> executable: Option<String>
    fn gen_optionized_fields(&self) -> Vec<TokenStream> {
        self.fields
            .iter()
            .map(|Fd { name, ty, .. }| quote! { #name: std::option::Option<#ty> })
            .collect()
    }

    // 为 XXXBuilder 生成处理函数
    // 比如：methods: fn executable(mut self, v: impl Into<String>) -> Self { self.executable = Some(v); self }
    fn gen_methods(&self) -> Vec<TokenStream> {
        self.fields
            .iter()
            .map(|Fd { name, ty, .. }| {
                quote! {
                    pub fn #name(mut self, v: impl Into<#ty>) -> Self {
                        self.#name = Some(v.into());
                        self
                    }
                }
            })
            .collect()
    }

    // 为 XXXBuilder 生成相应的赋值语句，把 XXXBuilder 每个字段赋值给 XXX 的字段
    // 比如：#field_name: self.#field_name.take().ok_or(" xxx need to be set!")
    fn gen_assigns(&self) -> Vec<TokenStream> {
        self.fields
            .iter()
            .map(|Fd { name, optional, .. }| {
                if *optional {
                    return quote! {
                        #name: self.#name.take()
                    };
                }

                quote! {
                    #name: self.#name.take().ok_or(concat!(stringify!(#name), " needs to be set!"))?
                }
            })
            .collect()
    }
}

// 如果是 T = Option<Inner>，返回 (true, Inner)；否则返回 (false, T)
fn get_option_inner(ty: &Type) -> (bool, &Type) {
    // 首先模式匹配出 segments
    if let Type::Path(TypePath {
        path: Path { segments, .. },
        ..
    }) = ty
    {
        if let Some(v) = segments.iter().next() {
            if v.ident == "Option" {
                // 如果 PathSegment 第一个是 Option，那么它内部应该是 AngleBracketed，比如 <T>
                // 获取其第一个值，如果是 GenericArgument::Type，则返回
                let t = match &v.arguments {
                    syn::PathArguments::AngleBracketed(a) => match a.args.iter().next() {
                        Some(GenericArgument::Type(t)) => t,
                        _ => panic!("Not sure what to do with other GenericArgument"),
                    },
                    _ => panic!("Not sure what to do with other PathArguments"),
                };
                return (true, t);
            }
        }
    }
    return (false, ty);
}

```

这段代码仔细阅读的话并不难理解，可能 `get_option_inner()` 拗口一些。你需要对着 DeriveInput 的 Debug 信息对应的部分比对着看，去推敲如何做模式匹配。比如：

```rust
ty: Path(
    TypePath {
        qself: None,
        path: Path {
            leading_colon: None,
            segments: [
                PathSegment {
                    ident: Ident {
                        ident: "Option",
                        span: #0 bytes(201..207),
                    },
                    arguments: AngleBracketed(
                        AngleBracketedGenericArguments {
                            colon2_token: None,
                            lt_token: Lt,
                            args: [
                                Type(
                                    Path(
                                        TypePath {
                                            qself: None,
                                            path: Path {
                                                leading_colon: None,
                                                segments: [
                                                    PathSegment {
                                                        ident: Ident {
                                                            ident: "String",
                                                            span: #0 bytes(208..214),
                                                        },
                                                        arguments: None,
                                                    },
                                                ],
                                            },
                                        },
                                    ),
                                ),
                            ],
                            gt_token: Gt,
                        },
                    ),
                },
            ],
        },
    },
),

```

这本身并不难，难的是心细以及足够的耐心。如果你对某个数据结构拿不准该怎么匹配，可以在 syn 的文档中查找这个数据结构，了解它的定义。

好，如果你理解了这个代码，我们就可以更新 src/lib.rs 里定义的 derive\_builder 了：

```rust
#[proc_macro_derive(Builder)]
pub fn derive_builder(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    builder::BuilderContext::from(input).render().into()
}

```

可以直接从 DeriveInput 中生成一个 BuilderContext，然后 render()。注意 quote 得到的是 proc\_macro2::TokenStream，所以需要调用一下 into() 转换成 proc\_macro::TokenStream。

在 examples/command.rs 中，更新 Command 的 derive 宏：

```rust
use macros::Builder;

#[allow(dead_code)]
#[derive(Debug, Builder)]
pub struct Command {
    ...
}

```

运行之，你可以得到正确的结果。

### one more thing：支持 attributes

很多时候，我们的派生宏可能还需要一些额外的 attributes 来提供更多信息，更好地指导代码的生成。比如 serde，你可以在数据结构中加入 #\[serde(xxx)\] attributes，控制 serde 序列化/反序列化的行为。

现在我们的 Builder 宏支持基本的功能，但用着还不那么特别方便，比如对于类型是 Vec 的 args，如果我可以依次添加每个 arg，该多好？

在 proc-macro-workshop 里 [Builder 宏的第 7 个练习](https://github.com/dtolnay/proc-macro-workshop/blob/master/builder/tests/07-repeated-field.rs) 中，就有这样一个需求：

```rust
#[derive(Builder)]
pub struct Command {
    executable: String,
    #[builder(each = "arg")]
    args: Vec<String>,
    #[builder(each = "env")]
    env: Vec<String>,
    current_dir: Option<String>,
}

fn main() {
    let command = Command::builder()
        .executable("cargo".to_owned())
        .arg("build".to_owned())
        .arg("--release".to_owned())
        .build()
        .unwrap();

    assert_eq!(command.executable, "cargo");
    assert_eq!(command.args, vec!["build", "--release"]);
}

```

这里，如果字段定义了 builder attributes，并且提供了 each 参数，那么用户不断调用 arg 来依次添加参数。这样使用起来，直观多了。

**分析一下这个需求。想要支持这样的功能，首先要能够解析 attributes，然后要能够根据 each attribute 的内容生成对应的代码**，比如这样：

```rust
pub fn arg(mut self, v: String) -> Self {
    let mut data = self.args.take().unwrap_or_default();
    data.push(v);
    self.args = Some(data);
    self
}

```

syn 提供的 DeriveInput 并没有对 attributes 额外处理，所有的 attributes 被包裹在一个 TokenTree::Group 中。

我们可以用上一讲提到的方法，手工处理 TokenTree/TokenStream，不过这样太麻烦，社区里已经有一个非常棒的库叫 [darling](https://github.com/teddriggs/darling)，光是名字就听上去惹人喜爱，用起来更是让人爱不释手。我们就使用这个库，来为 Builder 宏添加对 attributes 的支持。

为了避免对之前的 Builder 宏的破坏，我们把 src/builder.rs 拷贝一份出来改名 src/builder\_with\_attr.rs，然后在 src/lib.rs 中引用它。

在 src/lib.rs 中，我们再创建一个 BuilderWithAttrs 的派生宏：

```rust
#[proc_macro_derive(BuilderWithAttr, attributes(builder))]
pub fn derive_builder_with_attr(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    builder_with_attr::BuilderContext::from(input)
        .render()
        .into()
}

```

和之前不同的是，这里多了一个 attributes(builder) 属性，这是告诉编译器，请允许代码中出现的 `#[builder(...)]`，它是我这个宏认识并要处理的。

再创建一个 examples/command\_with\_attr.rs，把 workshop 中的代码粘进去并适当修改：

```rust
use macros::BuilderWithAttr;

#[allow(dead_code)]
#[derive(Debug, BuilderWithAttr)]
pub struct Command {
    executable: String,
    #[builder(each = "arg")]
    args: Vec<String>,
    #[builder(each = "env", default="vec![]")]
    env: Vec<String>,
    current_dir: Option<String>,
}

fn main() {
    let command = Command::builder()
        .executable("cargo".to_owned())
        .arg("build".to_owned())
        .arg("--release".to_owned())
        .build()
        .unwrap();

    assert_eq!(command.executable, "cargo");
    assert_eq!(command.args, vec!["build", "--release"]);
    println!("{:?}", command);
}

```

这里，我们不仅希望支持 each 属性，还支持 default —— 如果用户没有为这个域提供数据，就使用 default 对应的代码来初始化。

这个代码目前会报错，因为并未为 CommandBuilder 添加 arg 方法。接下来我们就要实现这个功能。

在 Cargo.toml 中，加入对 darling 的引用：

```rust
[dependencies]
darling = "0.13"

```

然后，在 src/builder\_with\_attr.rs 中，添加用于捕获 attributes 的数据结构：

```rust
use darling::FromField;

#[derive(Debug, Default, FromField)]
#[darling(default, attributes(builder))]
struct Opts {
    each: Option<String>,
    default: Option<String>,
}

```

因为我们捕获的是 field 级别的 attributes，所以这个数据结构需要实现 [FromField](https://docs.rs/darling/latest/darling/trait.FromField.html) trait（通过 FromTrait 派生宏），并且告诉 darling 要从哪个 attributes 中捕获（这里是从 builder 中捕获）。

不过先需要修改一下 Fd，让它包括 Opts，并且在 From 的实现中初始化 opts：

```rust
/// 我们需要的描述一个字段的所有信息
struct Fd {
    name: Ident,
    ty: Type,
    optional: bool,
    opts: Opts,
}

/// 把一个 Field 转换成 Fd
impl From<Field> for Fd {
    fn from(f: Field) -> Self {
        let (optional, ty) = get_option_inner(&f.ty);
        // 从 Field 中读取 attributes 生成 Opts，如果没有使用缺省值
        let opts = Opts::from_field(&f).unwrap_or_default();
        Self {
            opts,
            // 此时，我们拿到的是 NamedFields，所以 ident 必然存在
            name: f.ident.unwrap(),
            optional,
            ty: ty.to_owned(),
        }
    }
}

```

好，现在 Fd 就包含 Opts 的信息了，我们可以利用这个信息来生成 methods 和 assigns。

接下来先看 gen\_methods 怎么修改。如果 Fd 定义了 each attribute，且它是个 Vec 的话，我们就生成不一样的代码，否则的话，像之前那样生成代码。来看实现：

```rust
// 为 XXXBuilder 生成处理函数
// 比如：methods: fn executable(mut self, v: impl Into<String>) -> Self { self.executable = Some(v); self }
fn gen_methods(&self) -> Vec<TokenStream> {
    self.fields
        .iter()
        .map(|f| {
            let name = &f.name;
            let ty = &f.ty;
            // 如果不是 Option 类型，且定义了 each attribute
            if !f.optional && f.opts.each.is_some() {
                let each = Ident::new(f.opts.each.as_deref().unwrap(), name.span());
                let (is_vec, ty) = get_vec_inner(ty);
                if is_vec {
                    return quote! {
                        pub fn #each(mut self, v: impl Into<#ty>) -> Self {
                            let mut data = self.#name.take().unwrap_or_default();
                            data.push(v.into());
                            self.#name = Some(data);
                            self
                        }
                    };
                }
            }
            quote! {
                pub fn #name(mut self, v: impl Into<#ty>) -> Self {
                    self.#name = Some(v.into());
                    self
                }
            }
        })
        .collect()
}

```

这里，我们重构了一下 get\_option\_inner() 的代码，因为 get\_vec\_inner() 和它有相同的逻辑：

```rust
// 如果是 T = Option<Inner>，返回 (true, Inner)；否则返回 (false, T)
fn get_option_inner(ty: &Type) -> (bool, &Type) {
    get_type_inner(ty, "Option")
}

// 如果是 T = Vec<Inner>，返回 (true, Inner)；否则返回 (false, T)
fn get_vec_inner(ty: &Type) -> (bool, &Type) {
    get_type_inner(ty, "Vec")
}

fn get_type_inner<'a>(ty: &'a Type, name: &str) -> (bool, &'a Type) {
    // 首先模式匹配出 segments
    if let Type::Path(TypePath {
        path: Path { segments, .. },
        ..
    }) = ty
    {
        if let Some(v) = segments.iter().next() {
            if v.ident == name {
                // 如果 PathSegment 第一个是 Option/Vec 等类型，那么它内部应该是 AngleBracketed，比如 <T>
                // 获取其第一个值，如果是 GenericArgument::Type，则返回
                let t = match &v.arguments {
                    syn::PathArguments::AngleBracketed(a) => match a.args.iter().next() {
                        Some(GenericArgument::Type(t)) => t,
                        _ => panic!("Not sure what to do with other GenericArgument"),
                    },
                    _ => panic!("Not sure what to do with other PathArguments"),
                };
                return (true, t);
            }
        }
    }
    return (false, ty);
}

```

最后，我们为 gen\_assigns() 提供对 default attribute 的支持：

```rust
fn gen_assigns(&self) -> Vec<TokenStream> {
    self.fields
        .iter()
        .map(|Fd { name, optional, opts, .. }| {
            if *optional {
                return quote! {
                    #name: self.#name.take()
                };
            }

            // 如果定义了 default，那么把 default 里的字符串转换成 TokenStream
            // 使用 unwrap_or_else 在没有值的时候，使用缺省的结果
            if let Some(default) = opts.default.as_ref() {
                let ast: TokenStream = default.parse().unwrap();
                return quote! {
                    #name: self.#name.take().unwrap_or_else(|| #ast)
                };
            }

            quote! {
                #name: self.#name.take().ok_or(concat!(stringify!(#name), " needs to be set!"))?
            }
        })
        .collect()
}

```

如果你完成了这些改动，运行 `cargo run --example command_with_attr` 就会得到正确的结果。完整的代码，可以去 GitHub [repo](https://github.com/tyrchen/geektime-rust/tree/master/47_48_macros) 上获取。

## 小结

这一讲我们使用 syn/quote 重写了 Builder 派生宏的功能。可以看到，使用 syn/quote 后，宏的开发变得简单很多，最后我们还用 darling 进一步提供了对 attributes 的支持。

虽然这两讲我们只做了派生宏和一个非常简单的函数宏，但是，如果你学会了最复杂的派生宏，那开发函数宏和属性宏也不在话下。另外，darling 对 attributes 的支持，同样也可以应用在属性宏中。

今天重写Builder中核心做的就是，我们定义了两个自己的 From<T> trait，把 DeriveInput 转换成了自己的数据结构，然后围绕着我们自己的数据结构，构建更多的功能来生成代码。所以，宏编程不过是一系列数据结构的转换而已，并不神秘，它就跟我们平日里写的代码一样，只不过它操作和输出的数据结构都是语法树。

**使用宏来生成代码虽然听上去很牛，写起来也很有成就感，但是切不可滥用**。凡事都有两面，强大和灵活多变的对立面就是危险和难以捉摸。

因为虽然撰写宏并不困难，宏会为别人理解你的代码，使用你的代码带来额外的负担。由于宏会生成代码，大量使用宏会让你的代码在不知不觉中膨胀，也会导致二进制很大。另外，正如我们在使用中发现的那样，目前 IDE 对宏的支持还不够好，这也是大量使用宏的一个问题。我们看到像 [nom](https://github.com/Geal/nom) 这样的工具，一开始大量使用宏，后来也都逐渐用函数取代。

所以在开发的时候，要非常谨慎地构建宏。多问自己：我非用宏不可么？可以使用别的设计来避免使用宏么？同样是 Web 框架，rocket 使用宏做路由，axum 完全不使用宏。

就像 unsafe 一样，我们要把宏编程作为撰写代码最后的手段。 **当一个功能可以用函数表达时，不要用宏。不要过分迷信于编译时的处理，不要把它当成提高性能的手段**。如果你发现某个设计似乎不得不使用宏，你需要质疑一下，自己设计上的选择是否正确。

### 思考题

学完了这两课，如果你还觉得不过瘾，可以继续完成 [proc-macro-workshop](https://github.com/dtolnay/proc-macro-workshop) 里Builder 以外的其它例子。这些例子你耐心地把它们全做一遍，一定会有很大的收获。

学习愉快，如果你觉得有收获，也欢迎你分享给你身边的朋友，邀他一起讨论。